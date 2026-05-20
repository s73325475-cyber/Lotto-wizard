import requests
import json
import time
from datetime import date
import re
from bs4 import BeautifulSoup

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
        url = f'https://www.dhlottery.co.kr/gameResult.do?method=byWinNo&drwNo={no}'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'status {no}: {r.status_code}')
        
        if r.status_code != 200:
            print(f'error {no}: 페이지 로드 실패')
            break
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 회차 검증 (안전장치)
        meta_title = soup.find('meta', {'property': 'og:title'})
        if not meta_title or f"{no}회" not in meta_title.get('content', ''):
            print(f'no data {no}: {no}회차 결과 페이지를 찾을 수 없습니다.')
            break
            
        # 당첨번호 6개와 보너스 번호 추출 (선택자 보강)
        num_balls = soup.select('.win_result .num.win span.ball_645')
        bonus_ball = soup.select_one('.win_result .num.bonus span.ball_645')
        date_match = soup.select_one('.win_result p.desc')
        
        if len(num_balls) == 6 and bonus_ball:
            drwtNo = [int(ball.text) for ball in num_balls]
            bnusNo = int(bonus_ball.text)
            
            # 날짜 정제 (YYYY-MM-DD 형태 만들기)
            date_str = today.isoformat()
            if date_match:
                raw_date = date_match.text
                extracted = re.findall(r'\d+', raw_date)
                if len(extracted) >= 3:
                    date_str = f"{extracted[0]}-{extracted[1].zfill(2)}-{extracted[2].zfill(2)}"

            # 데이터 추가 (오타 수정 반영)
            draws.append({
                'drwNo': no,
                'drwNoDate': date_str,
                'drwtNo1': drwtNo[0],
                'drwtNo2': drwtNo[1],
                'drwtNo3': drwtNo[2],
                'drwtNo4': drwtNo[3],
                'drwtNo5': drwtNo[4],
                'drwtNo6': drwtNo[5],  # ◀ drwtNo[6-1] 오타를 [5]로 직관적으로 수정
                'bnusNo': bnusNo,
                'firstPrzwnerCo': 0,
                'firstWinamnt': 0
            })
            added += 1
            print(f'added: {no}')
        else:
            print(f'parse fail {no}: 번호 영역을 찾지 못했습니다. 추출된 개수: {len(num_balls)}')
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
