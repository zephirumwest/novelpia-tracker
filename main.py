# main.py (Upgraded Version)

import pandas as pd
import schedule
import time
from datetime import datetime
from scraper import get_novel_stats

CSV_FILE = 'stats.csv'

def job():
    print(f"\n{'='*10} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 작업을 시작합니다. {'='*10}")

    current_stats = get_novel_stats()
    if not current_stats:
        print("Main: 데이터를 가져오는 데 실패하여 이번 주기는 건너뜁니다.")
        return

    print(f"Main: 현재 조회수 - 1화({current_stats['ep1_views']}), 최신화({current_stats['latest_ep_views']})")

    # 변동량 변수를 0으로 초기화
    ep1_diff = 0
    latest_ep_diff = 0
    
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("Main: stats.csv 파일이 없어 새로 생성합니다.")
        # !! 변경점: 새로운 컬럼 이름으로 데이터프레임 생성
        df = pd.DataFrame(columns=['date', 'ep1_views', 'ep1_diff', 'latest_ep_views', 'latest_ep_diff'])

    if not df.empty:
        last_row = df.iloc[-1]
        ep1_diff = current_stats['ep1_views'] - last_row['ep1_views']
        latest_ep_diff = current_stats['latest_ep_views'] - last_row['latest_ep_views']

        print("\n--- 직전 기록 대비 변화량 ---")
        print(f"📈 총 유입 (1화 조회수): {ep1_diff:+,}")
        print(f"🚀 최신화 성장세: {latest_ep_diff:+,}")
        print("---------------------------\n")

    # !! 변경점: 오늘 날짜를 YYYY-MM-DD 형식으로 저장
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # !! 변경점: 새로운 5개 컬럼에 맞춰 데이터 행 생성
    new_row = pd.DataFrame([{
        'date': today_date,
        'ep1_views': current_stats['ep1_views'],
        'ep1_diff': ep1_diff,
        'latest_ep_views': current_stats['latest_ep_views'],
        'latest_ep_diff': latest_ep_diff
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    print(f"Main: '{CSV_FILE}' 파일에 새로운 데이터를 저장했습니다.")
    print(f"{'='*12} 작업 완료. 다음 실행을 기다립니다. {'='*12}")

# --- (스케줄러 실행 부분은 이전과 동일) ---
if __name__ == "__main__":
    job()
    schedule.every(1).minutes.do(job)
    print("="*50)
    print("🚀 [업그레이드 버전] 조회수 트래커가 시작되었습니다.")
    print("="*50)
    while True:
        schedule.run_pending()
        time.sleep(1)