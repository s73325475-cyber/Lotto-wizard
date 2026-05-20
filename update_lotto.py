import requests
import json
import sys
from datetime import datetime

# 🔗 파이어베이스 실시간 데이터베이스 URL
FIREBASE_URL = "https://lotto-wizard-52ee4-default-rtdb.asia-southeast1.firebasedatabase.app/.json"

def load_lotto_data():
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200 and response.json():
            return response.json()
    except Exception as e:
        print(f"파이어베이스 데이터 로드 실패: {e}")
    return {"lastUpdated": "", "totalDraws": 0, "draws": []}

def save_lotto_data(data):
    try:
        data['draws'].sort(key=lambda x: x['drwNo'])
        data['totalDraws'] = len(data['draws'])
        data['lastUpdated'] = datetime.now().date().isoformat()
        
        response = requests.put(FIREBASE_URL, json=data)
        if response.status_code == 200:
            print("🚀 파이어베이스 서버에 데이터가 성공적으로 저장되었습니다!")
            return True
    except Exception as e:
        print(f"파이어베이스 데이터 저장 실패: {e}")
        return False

if __name__ == "__main__":
    # 깃허브 액션에서 인자값으로 번호들을 넘겨받음
    if len(sys.argv) < 9:
        print("⚠️ 입력된 데이터가 부족합니다. 깃허브 액션을 통해 실행해 주세요.")
        sys.exit(1)
        
    try:
        # 깃허브 액션이 전달해 준 값을 순서대로 매칭
        drwNoDate = sys.argv[1].strip()
        n1 = int(sys.argv[2])
        n2 = int(sys.argv[3])
        n3 = int(sys.argv[4])
        n4 = int(sys.argv[5])
        n5 = int(sys.argv[6])
        n6 = int(sys.argv[7])
        bnus = int(sys.argv[8])
        
        # 파이어베이스 데이터 로드
        lotto_data = load_lotto_data()
        draws_list = lotto_data.get('draws', [])
        
        # 다음 회차 자동 계산
        next_no = (draws_list[-1]['drwNo'] + 1) if draws_list else 1
        print(f"새로 추가될 회차: {next_no}회")
        
        # 중복 검증 및 결합
        if any(x['drwNo'] == next_no for x in draws_list):
            print("⚠️ 이미 파이어베이스에 존재하는 회차입니다!")
        else:
            new_draw = {
                "drwNo": int(next_no),
                "drwNoDate": drwNoDate,
                "drwtNo1": n1, "drwtNo2": n2, "drwtNo3": n3,
                "drwtNo4": n4, "drwtNo5": n5, "drwtNo6": n6,
                "bnusNo": bnus,
                "firstPrzwnerCo": 0, "firstWinamnt": 0
            }
            draws_list.append(new_draw)
            lotto_data['draws'] = draws_list
            
            # 파이어베이스로 최종 전송
            save_lotto_data(lotto_data)
            
    except Exception as e:
        print(f"데이터 처리 중 오류 발생: {e}")
