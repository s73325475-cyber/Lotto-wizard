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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

added = 0
for no in range(max_no + 1, est + 1):
    try:
        # 공공 데이터 기반의 가장 안정적인 로또 전용 오픈 데이터 주소
        url = f'https://open.api.ncloud-hub.com/v1/lotto/drwNo/{no}'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            # 2차 예비 안정화 허브 주소
            url = f'https://raw.githubusercontent.com/seous/lotto-json/main/data/{no}.json'
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f'error {no}: 모든 데이터 허브 연결 실패')
                break

        d = r.json()
        
        # 데이터가 정상적인 구조인지 체크
        if 'drwNo' in d and 'drwtNo1' in d:
            draws.append({
                'drwNo': int(d['drwNo']),
                'drwNoDate': d.get('drwNoDate', today.isoformat()),
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
            print(f'invalid data format: {no}')
            break
            
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
