# scraper.py (Cleaned Version)

import time
import logging  # logging 기능 자체는 필요하므로 import는 유지
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NOVEL_ID = "370230"
BASE_URL = "https://novelpia.com/"
NOVEL_URL = f"{BASE_URL}novel/{NOVEL_ID}"

def get_novel_stats():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(NOVEL_URL)
        
        logging.info("페이지 로딩 및 '첫화부터' 정렬 상태 확인 중...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#episode_list tr.ep_style5"))
        )
        
        first_ep_element_before_sort = driver.find_element(By.CSS_SELECTOR, "#episode_list tr.ep_style5")
        soup_page1 = BeautifulSoup(driver.page_source, 'html.parser')
        ep1_views = int(soup_page1.select_one("#episode_list tr.ep_style5 span.episode_count_view").text.replace(',', ''))
        
        logging.info("'첫화부터 ↓↑' 정렬 버튼 클릭 중...")
        sort_button = driver.find_element(By.CSS_SELECTOR, "div.toggle_sort")
        driver.execute_script("arguments[0].click();", sort_button)
        
        logging.info("정렬 변경 대기 중...")
        WebDriverWait(driver, 15).until(EC.staleness_of(first_ep_element_before_sort))
        logging.info("정렬 변경 완료. '최신화부터' 상태.")

        soup_latest = BeautifulSoup(driver.page_source, 'html.parser')
        all_episodes = soup_latest.select("#episode_list tr.ep_style5")
        
        if not all_episodes:
            logging.error("일반 회차 목록을 찾을 수 없습니다!")
            return None

        latest_ep_element = all_episodes[0]
        latest_ep_title = latest_ep_element.select_one("td.font12 > b").text.strip()
        latest_ep_views = int(latest_ep_element.select_one("span.episode_count_view").text.replace(',', ''))
        
        logging.info(f"타겟 1순위 회차: '{latest_ep_title}', 조회수: {latest_ep_views}")

        if latest_ep_views == 0 and len(all_episodes) > 1:
            logging.warning("조회수가 0으로 감지되어 예비 타겟을 확인합니다.")
            fallback_ep_element = all_episodes[1]
            fallback_ep_title = fallback_ep_element.select_one("td.font12 > b").text.strip()
            fallback_ep_views = int(fallback_ep_element.select_one("span.episode_count_view").text.replace(',', ''))
            logging.info(f"예비 타겟 회차: '{fallback_ep_title}', 조회수: {fallback_ep_views}")
            latest_ep_views = fallback_ep_views

        return { "ep1_views": ep1_views, "latest_ep_views": latest_ep_views }

    except Exception as e:
        logging.error(f"스크래핑 중 심각한 오류 발생: {e}", exc_info=True)
        return None
    finally:
        if driver:
            driver.quit()