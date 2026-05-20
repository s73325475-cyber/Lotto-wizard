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

# 차단 없는 공공/외부 오픈 API 주소 활용
added = 0
for no in range(max_no + 1, est + 1):
    try:
        # 동행복권 본사 서버가 아닌, 우회 가능한 로또 오픈 API 주소 사용
        url = f'https://api.lotto.chal6.com/v1/lotto?drwNo={no}'
        r = requests.get(url, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            print(f'error {no}: 데이터를 가져오지 못했습니다.')
            break
            
        d = r.json()
        # API 제공 형식에 맞춰 성공 여부 체크
        if d.get('returnValue') == 'success' or 'drwNo' in d:
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
                'firstPrzwnerCo': d.get('firstPrzwnerCo', 0),
                'firstWinamnt': d.get('firstWinamnt', 0)
            })
            added += 1
            print(f'added: {no}')
        else:
            print(f'no data: {no}')
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
