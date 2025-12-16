# main.py (Robust Version)

import pandas as pd
from datetime import datetime
from scraper import get_novel_stats # 업그레이드된 scraper를 가져옵니다.
import logging # 로깅을 위해 추가

# main.py에서도 로그를 남기도록 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()])

CSV_FILE = 'stats.csv'

def job():
    logging.info(f"\n{'='*10} 작업을 시작합니다. {'='*10}")

    current_stats = get_novel_stats()
    if not current_stats:
        logging.error("데이터를 가져오는 데 실패하여 이번 주기는 건너뜁니다.")
        exit(1) # GitHub Actions에서 실패로 표시되도록 종료

    logging.info(f"최종 집계된 조회수 - 1화({current_stats['ep1_views']}), 최신화({current_stats['latest_ep_views']})")

    # (이하 CSV 저장 로직은 이전과 동일)
    ep1_diff = 0
    latest_ep_diff = 0
    
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        logging.info("stats.csv 파일이 없어 새로 생성합니다.")
        df = pd.DataFrame(columns=['date', 'ep1_views', 'ep1_diff', 'latest_ep_views', 'latest_ep_diff'])

    if not df.empty:
        last_row = df.iloc[-1]
        ep1_diff = current_stats['ep1_views'] - last_row['ep1_views']
        latest_ep_diff = current_stats['latest_ep_views'] - last_row['latest_ep_views']

        logging.info("\n--- 직전 기록 대비 변화량 ---")
        logging.info(f"📈 총 유입 (1화 조회수): {ep1_diff:+,}")
        logging.info(f"🚀 최신화 성장세: {latest_ep_diff:+,}")
        logging.info("---------------------------\n")

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
    logging.info(f"'{CSV_FILE}' 파일에 새로운 데이터를 저장했습니다.")
    logging.info(f"{'='*12} 작업 완료. {'='*12}")

if __name__ == "__main__":
    job()