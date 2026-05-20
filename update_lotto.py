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

# GitHub 가상 서버가 아닌, 실제 스마트폰 앱에서 요청하는 것처럼 위장하는 완벽한 헤더 값 세팅
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://m.dhlottery.co.kr',
    'Referer': 'https://m.dhlottery.co.kr/'
}

added = 0
for no in range(max_no + 1, est + 1):
    try:
        # [핵심] 차단 필터링이 덜한 동행복권 모바일 전용 데이터 허브 API 주소로 직접 찌릅니다.
        url = f'https://m.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={no}'
        
        r = requests.get(url, headers=headers, timeout=10)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            print(f'error {no}: 동행복권 모바일 서버 연결 실패')
            break
            
        d = r.json()
        
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
            print(f'no data on server: {no}')
            break
            
        time.sleep(1)
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
