# scraper.py (Simple Retry Version)

import time
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# NOVEL_ID = "370230"
# BASE_URL = "https://novelpia.com/"
# NOVEL_URL = f"{BASE_URL}novel/{NOVEL_ID}"

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
            
            # 제목 확인 (로그용)
            title_temp = first_row.select_one("td.font12 > b").text.strip()
            logging.info(f"1화 조회수({ep1_views}) 확인. (제목: {title_temp})")

            # 3. 정렬 변경
            logging.info("'첫화부터 ↓↑' 정렬 버튼 클릭...")
            sort_button = driver.find_element(By.CSS_SELECTOR, "div.toggle_sort")
            driver.execute_script("arguments[0].click();", sort_button)
            
            # [핵심] 복잡한 대기 다 빼고, 그냥 2초 쉽니다. (옛날 방식)
            # 어차피 안 바뀌었으면 0이거나 1화 조회수가 나올 테니 아래에서 걸러집니다.
            logging.info("정렬 반영 대기 중 (2초)...")
            time.sleep(2)

            # 4. 최신화 정보 확인
            soup_latest = BeautifulSoup(driver.page_source, 'html.parser')
            all_episodes = soup_latest.select("#episode_list tr[data-episode-no]")
            
            if not all_episodes:
                raise Exception("회차 목록을 찾을 수 없음")

            latest_ep_element = all_episodes[0]
            latest_ep_title = latest_ep_element.select_one("td.font12 > b").text.strip()
            latest_ep_views = int(latest_ep_element.select_one("span.episode_count_view").text.replace(',', ''))
            
            logging.info(f"확인된 최신화: '{latest_ep_title}', 조회수: {latest_ep_views}")

            # 5. [체크] 조회수가 0이거나, 정렬이 안 돼서 1화랑 제목이 똑같으면 재시도
            if latest_ep_views == 0:
                logging.warning(f"⚠️ 조회수 0 감지! (시도 {attempt})")
                raise Exception("조회수가 0입니다.") # 강제로 에러를 발생시켜 재시도 로직으로 보냄
            
            if latest_ep_title == title_temp:
                 logging.warning(f"⚠️ 정렬이 안 된 것 같습니다. (제목이 1화랑 같음) (시도 {attempt})")
                 raise Exception("정렬 실패 의심")

            # 여기까지 오면 성공!
            return { "ep1_views": ep1_views, "latest_ep_views": latest_ep_views }

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