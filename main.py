# main.py (GitHub Actions Version)

import pandas as pd
from datetime import datetime
from scraper import get_novel_stats

CSV_FILE = 'stats.csv'

def job():
    print(f"\n{'='*10} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 작업을 시작합니다. {'='*10}")

    current_stats = get_novel_stats()
    if not current_stats:
        print("Main: 데이터를 가져오는 데 실패했습니다.")
        # 실패 시 비정상 종료 코드를 반환하여 GitHub Actions에 알림
        exit(1)

    print(f"Main: 현재 조회수 - 1화({current_stats['ep1_views']}), 최신화({current_stats['latest_ep_views']})")

    ep1_diff = 0
    latest_ep_diff = 0
    
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("Main: stats.csv 파일이 없어 새로 생성합니다.")
        df = pd.DataFrame(columns=['date', 'ep1_views', 'ep1_diff', 'latest_ep_views', 'latest_ep_diff'])

    if not df.empty:
        last_row = df.iloc[-1]
        ep1_diff = current_stats['ep1_views'] - last_row['ep1_views']
        latest_ep_diff = current_stats['latest_ep_views'] - last_row['latest_ep_views']

        print("\n--- 직전 기록 대비 변화량 ---")
        print(f"📈 총 유입 (1화 조회수): {ep1_diff:+,}")
        print(f"🚀 최신화 성장세: {latest_ep_diff:+,}")
        print("---------------------------\n")

    today_date = datetime.now().strftime('%Y-%m-%d')
    
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
    print(f"{'='*12} 작업 완료. {'='*12}")

# --- 이 스크립트가 실행되면 job() 함수를 딱 한 번만 호출하고 종료 ---
if __name__ == "__main__":
    job()