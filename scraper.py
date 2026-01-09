# scraper.py (Hybrid: Retry + Fallback Version)

import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NOVEL_ID = "370230"
BASE_URL = "https://novelpia.com/"
NOVEL_URL = f"{BASE_URL}novel/{NOVEL_ID}"
MAX_RETRIES = 3

def get_novel_stats():
    for attempt in range(1, MAX_RETRIES + 1):
        logging.info(f"========== 스크래핑 시도 {attempt}/{MAX_RETRIES} ==========")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

        driver = None
        try:
            # 1. 브라우저 열기
            driver = webdriver.Chrome(options=options)
            driver.get(NOVEL_URL)
            
            # 페이지 로딩 대기
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#episode_list tr[data-episode-no]"))
            )
            
            # 2. 1화 정보 가져오기
            soup_page1 = BeautifulSoup(driver.page_source, 'html.parser')
            first_row = soup_page1.select_one("#episode_list tr[data-episode-no]")
            ep1_views = int(first_row.select_one("span.episode_count_view").text.replace(',', ''))
            
            title_temp = first_row.select_one("td.font12 > b").text.strip()
            logging.info(f"1화 조회수({ep1_views}) 확인. (제목: {title_temp})")

            # 3. 정렬 변경
            logging.info("'첫화부터 ↓↑' 정렬 버튼 클릭...")
            sort_button = driver.find_element(By.CSS_SELECTOR, "div.toggle_sort")
            driver.execute_script("arguments[0].click();", sort_button)
            
            logging.info("정렬 반영 대기 중 (2초)...")
            time.sleep(2)

            # 4. 최신화 정보 확인
            soup_latest = BeautifulSoup(driver.page_source, 'html.parser')
            all_episodes = soup_latest.select("#episode_list tr[data-episode-no]")
            
            if not all_episodes:
                raise Exception("회차 목록을 찾을 수 없음")

            # 1순위: 맨 위 회차
            target_ep = all_episodes[0]
            target_title = target_ep.select_one("td.font12 > b").text.strip()
            target_views = int(target_ep.select_one("span.episode_count_view").text.replace(',', ''))
            
            logging.info(f"타겟 회차(1순위): '{target_title}', 조회수: {target_views}")

            # 5. [핵심] 조회수가 0일 때의 분기 처리
            if target_views == 3275:
                logging.warning(f"⚠️ 최신화 조회수가 0입니다. 원인 분석 중...")

                # 2순위: 그 바로 아래 회차 확인 (Fallback)
                if len(all_episodes) > 1:
                    fallback_ep = all_episodes[1]
                    fallback_title = fallback_ep.select_one("td.font12 > b").text.strip()
                    fallback_views = int(fallback_ep.select_one("span.episode_count_view").text.replace(',', ''))
                    
                    logging.info(f"예비 회차(2순위): '{fallback_title}', 조회수: {fallback_views}")

                    if fallback_views > 4000:
                        logging.info(">>> [판단] 실행 지연으로 새 회차를 가져온 것 같습니다. 예비 회차 데이터를 사용합니다.")
                        # 예비 회차 데이터를 최종 데이터로 채택 (성공!)
                        target_views = fallback_views
                        # target_title = fallback_title (제목은 기록용이라 굳이 안 바꿔도 됨)
                    else:
                        logging.warning(">>> [판단] 예비 회차도 조회수가 0입니다. 서버 오류나 로딩 실패로 보입니다.")
                        raise Exception("1순위, 2순위 모두 조회수 0") # 강제 재시도
                else:
                    # 회차가 1개뿐인데 0이면 방법이 없음
                    raise Exception("회차가 하나뿐인데 조회수가 0")

            # 6. 정렬 실패 체크 (제목이 1화랑 같으면)
            if target_title == title_temp:
                 logging.warning(f"⚠️ 정렬이 안 된 것 같습니다. (제목이 1화랑 같음) (시도 {attempt})")
                 raise Exception("정렬 실패 의심")

            # 여기까지 오면 성공! (0이었어도 fallback으로 대체되었거나, 원래 정상이거나)
            return { "ep1_views": ep1_views, "latest_ep_views": target_views }

        except Exception as e:
            logging.error(f"오류 발생 또는 재시도 필요: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = None
            
            if attempt < MAX_RETRIES:
                logging.info(">>> 브라우저를 닫고 5초 후 다시 시도합니다...")
                time.sleep(5)
                continue
            else:
                logging.error("최대 재시도 횟수 초과. 실패.")
                return None
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    return None