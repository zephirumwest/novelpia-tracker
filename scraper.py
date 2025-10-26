# scraper.py

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NOVEL_ID = "370230"
BASE_URL = "https://novelpia.com/"
NOVEL_URL = f"{BASE_URL}novel/{NOVEL_ID}"

def get_novel_stats():
    """
    노벨피아에 접속하여 1화와 최신화의 조회수를 스크래핑하는 함수.
    성공 시 {'ep1_views': 123, 'latest_ep_views': 456} 형태의 딕셔너리를 반환.
    실패 시 None을 반환.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(NOVEL_URL)
        
        print("Scraper: 페이지 로딩 및 '첫화부터' 정렬 상태 확인 중...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "episode_list"))
        )
        
        first_ep_element_before_sort = driver.find_element(By.CSS_SELECTOR, "#episode_list div.ep_style2")

        soup_page1 = BeautifulSoup(driver.page_source, 'html.parser')
        ep1_views = int(soup_page1.select_one("#episode_list div.ep_style2 span.episode_count_view").text.replace(',', ''))
        
        print("Scraper: '첫화부터 ↓↑' 정렬 버튼 클릭 중...")
        sort_button = driver.find_element(By.CSS_SELECTOR, "div.toggle_sort")
        driver.execute_script("arguments[0].click();", sort_button)
        
        print("Scraper: 정렬 변경 대기 중...")
        WebDriverWait(driver, 10).until(
            EC.staleness_of(first_ep_element_before_sort)
        )

        soup_latest = BeautifulSoup(driver.page_source, 'html.parser')
        latest_ep_views = int(soup_latest.select_one("#episode_list div.ep_style2 span.episode_count_view").text.replace(',', ''))
        
        return { "ep1_views": ep1_views, "latest_ep_views": latest_ep_views }

    except Exception as e:
        print(f"Scraper: 스크래핑 중 오류 발생 - {e}")
        return None
    finally:
        if driver:
            driver.quit()