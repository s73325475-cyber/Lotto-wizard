import requests
import json
from datetime import datetime

# 🔗 파이어베이스 실시간 데이터베이스 URL
FIREBASE_URL = "https://lotto-wizard-52ee4-default-rtdb.asia-southeast1.firebasedatabase.app/lotto.json"

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
    # 1. 기존 파이어베이스 데이터 원격 로드
    lotto_data = load_lotto_data()
    draws_list = lotto_data.get('draws', [])
    
    # 2. 다음 입력할 회차 자동 계산 (1223 다음은 1224)
    next_no = (draws_list[-1]['drwNo'] + 1) if draws_list else 1
    print(f"\n현재 등록된 최신 회차: {next_no - 1}회")
    print(f"--- {next_no}회 당첨번호 수동 입력 시작 ---")
    
    # 3. 터미널(콘솔)에서 직접 번호 받기
    # ⚠️ 주의: 깃허브 액션 수동 실행 시 입력창 대용으로 쓰입니다.
    try:
        drwNoDate = input("추첨 날짜를 입력하세요 (예: 2026-05-23): ").strip()
        n1 = int(input("번호 1: "))
        n2 = int(input("번호 2: "))
        n3 = int(input("번호 3: "))
        n4 = int(input("번호 4: "))
        n5 = int(input("번호 5: "))
        n6 = int(input("번호 6: "))
        bnus = int(input("보너스 번호: "))
        
        # 중복 검증
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
            
            # 파이어베이스 전송
            save_lotto_data(lotto_data)
            
    except Exception as e:
        print(f"입력 오류 또는 강제 종료: {e}")
