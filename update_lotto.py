import requests
import json
import time
from datetime import date

with open('lotto.json', 'r') as f:
    data = json.load(f)

draws = data['draws']
nos = set(d['drwNo'] for d in draws)
max_no = max(nos) if nos else 0
today = date.today()
est = (today - date(2002, 12, 7)).days // 7 + 1

print(f'max saved: {max_no}, estimated latest: {est}')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://www.dhlottery.co.kr/'
}

added = 0
for no in range(max_no + 1, est + 2):
    try:
        url = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=' + str(no)
        r = requests.get(url, headers=headers, timeout=15)
        print(f'status {no}: {r.status_code}')
        d = r.json()
        if d.get('returnValue') == 'success':
            draws.append({
                'drwNo': d['drwNo'],
                'drwNoDate': d['drwNoDate'],
                'drwtNo1': d['drwtNo1'],
                'drwtNo2': d['drwtNo2'],
                'drwtNo3': d['drwtNo3'],
                'drwtNo4': d['drwtNo4'],
                'drwtNo5': d['drwtNo5'],
                'drwtNo6': d['drwtNo6'],
                'bnusNo': d['bnusNo'],
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

draws.sort(key=lambda x: x['drwNo'])
with open('lotto.json', 'w') as f:
    json.dump({
        'lastUpdated': today.isoformat(),
        'totalDraws': len(draws),
        'draws': draws
    }, f, ensure_ascii=True, separators=(',', ':'))

print(f'done: added {added}, total {len(draws)}')
