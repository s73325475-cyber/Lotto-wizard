import requests
import json
import time
from datetime import date

# 1. 기존 데이터 로드
with open('lotto.json', 'r') as f:
    data = json.load(f)

draws = data['draws']
nos = set(d['drwNo'] for d in draws)
max_no = max(nos) if nos else 0
today = date.today()
est = (today - date(2002, 12, 7)).days // 7 + 1

print(f'max saved: {max_no}, estimated latest: {est}')

# 브라우저 기본 헤더 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

added = 0
for no in range(max_no + 1, est + 1):
    try:
        # 절대 죽지 않는 대기업(다음/네이버 검색 연동형) 로또 데이터 허브 주소 활용
        url = f'https://search.daum.net/ke/lotto/drwNo/{no}'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            # 다음 주소가 실패할 경우 네이버 검색 백업 주소로 2차 시도
            url = f'https://m.search.naver.com/p/csearch/content/qapidb.nhn?_callback=window.__jindo2_callback._lotto_info_0&q=로또+{no}회+당첨번호'
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f'error {no}: 데이터 소스 로드 실패')
                break
                
            # 네이버 데이터 정제 (JSON 추출)
            json_text = r.text.split('_lotto_info_0(')[1].split(');')[0]
            raw_data = json.loads(json_text)
            
            # 네이버 데이터 구조 분석 후 주입
            lotto_info = raw_data['items'][0]
            draws.append({
                'drwNo': no,
                'drwNoDate': lotto_info['txt2'].replace('.', '-'),
                'drwtNo1': int(lotto_info['num1']),
                'drwtNo2': int(lotto_info['num2']),
                'drwtNo3': int(lotto_info['num3']),
                'drwtNo4': int(lotto_info['num4']),
                'drwtNo5': int(lotto_info['num5']),
                'drwtNo6': int(lotto_info['num6']),
                'bnusNo': int(lotto_info['num7']),
                'firstPrzwnerCo': 0,
                'firstWinamnt': 0
            })
            added += 1
            print(f'added from naver: {no}')
            continue

        # 다음(Daum) 데이터가 정상 처리되었을 때
        d = r.json()
        draws.append({
            'drwNo': no,
            'drwNoDate': d.get('drwNoDate', today.isoformat()),
            'drwtNo1': int(d['drwtNo1']),
            'drwtNo2': int(d['drwtNo2']),
            'drwtNo3': int(d['drwtNo3']),
            'drwtNo4': int(d['drwtNo4']),
            'drwtNo5': int(d['drwtNo5']),
            'drwtNo6': int(d['drwtNo6']),
            'bnusNo': int(d['bnusNo']),
            'firstPrzwnerCo': d.get('firstPrzwnerCo', 0),
            'firstWinamnt': d.get('firstWinamnt', 0)
        })
        added += 1
        print(f'added from daum: {no}')
            
        time.sleep(1.5)
    except Exception as e:
        print(f'error {no}: {e}')
        break

# 3. 데이터 정렬 및 저장
draws.sort(key=lambda x: x['drwNo'])
with open('lotto.json', 'w') as f:
    json.dump({
        'lastUpdated': today.isoformat(),
        'totalDraws': len(draws),
        'draws': draws
    }, f, ensure_ascii=True, separators=(',', ':'))

print(f'done: added {added}, total {len(draws)}')
