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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://www.dhlottery.co.kr/'
}

added = 0
for no in range(max_no + 1, est + 1):
    try:
        # [핵심] GitHub IP 차단을 우회하기 위해 무료 프록시 게이트웨이(Allorigins)를 거쳐 동행복권 공식 API 호출
        target_url = f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={no}'
        url = f'https://api.allorigins.win/get?url={requests.utils.quote(target_url)}'
        
        r = requests.get(url, headers=headers, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            print(f'error {no}: 우회 서버 응답 실패')
            break
            
        # 프록시 서버는 결과를 원래 데이터 포맷을 싼 json 형태로 줍니다.
        wrapper_data = r.json()
        # 그 안에서 진짜 동행복권이 준 데이터를 꺼내 파싱합니다.
        d = json.loads(wrapper_data['contents'])
        
        if d.get('returnValue') == 'success':
            draws.append({
                'drwNo': int(d['drwNo']),
                'drwNoDate': d['drwNoDate'],
                'drwtNo1': int(d['drwtNo1']),
                'drwtNo2': int(d['drwtNo2']),
                'drwtNo3': int(d['drwtNo3']),
                'drwtNo4': int(d['drwtNo4']),
                'drwtNo5': int(d['drwtNo5']),
                'drwtNo6': int(d['drwtNo6']),
                'bnusNo': int(d['bnusNo']),
                'firstPrzwnerCo': int(d.get('firstPrzwnerCo', 0)),
                'firstWinamnt': int(d.get('firstWinamnt', 0))
            })
            added += 1
            print(f'added: {no}')
        else:
            print(f'no data on official server: {no}')
            break
            
        time.sleep(2)
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
