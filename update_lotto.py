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

# 2. 브라우저처럼 완벽하게 위장하기 위한 세션 및 헤더 설정
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://www.dhlottery.co.kr/common.do?method=main',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive'
}
session.headers.update(headers)

added = 0
# 미래 회차까지 불필요하게 돌지 않도록 범위를 est + 1 정도로 조절
for no in range(max_no + 1, est + 1):
    try:
        url = f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={no}'
        r = session.get(url, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        # [핵심 안전장치] 만약 받아온 내용이 JSON이 아니라 HTML(글자)이면 예외 처리로 보냄
        if not r.text.strip().startswith('{'):
            print(f'error {no}: 응답이 JSON 형식이 아닙니다. 차단되었거나 페이지가 변경되었을 수 있습니다.')
            break
            
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
        
        # 연속 요청 시 차단 방지를 위해 조금 여유 있게 대기 (2초)
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
