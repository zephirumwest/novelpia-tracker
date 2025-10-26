# novelpia.py (Sort Button Click Version - THE REAL FINAL)

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 기본 설정 ---
NOVEL_ID = "370230"
BASE_URL = "https://novelpia.com/"
NOVEL_URL = f"{BASE_URL}novel/{NOVEL_ID}"

def get_novel_stats():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # 테스트 중에는 이 줄을 주석 처리해서 눈으로 직접 보세요!
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(NOVEL_URL)
        
        # --- 1. 첫화 조회수 가져오기 (기본 정렬 상태) ---
        print("페이지 로딩 및 '첫화부터' 정렬 상태 확인 중...")
        # 회차 목록 전체를 감싸는 id="episode_list"가 나타날 때까지 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "episode_list"))
        )
        
        # 페이지 전환 확인을 위해, 현재 1화의 웹 요소를 미리 저장해둡니다.
        first_ep_element_before_sort = driver.find_element(By.CSS_SELECTOR, "#episode_list div.ep_style2")

        soup_page1 = BeautifulSoup(driver.page_source, 'html.parser')
        ep1_views = int(soup_page1.select_one("#episode_list div.ep_style2 span.episode_count_view").text.replace(',', ''))
        print(f"✅ 1화 조회수 (첫화부터 정렬): {ep1_views}")

        # --- 2. 정렬 버튼 클릭 ---
        print("'첫화부터 ↓↑' 정렬 버튼을 찾습니다...")
        # !! 중요 !!: 스크린샷에서 확인된 `div.toggle_sort` 선택자 사용
        sort_button = driver.find_element(By.CSS_SELECTOR, "div.toggle_sort")
        
        print("정렬 버튼을 클릭하여 '최신화부터'로 변경합니다...")
        driver.execute_script("arguments[0].click();", sort_button)

        # --- 3. 정렬이 바뀔 때까지 기다리기 ---
        print("정렬이 변경되기를 기다립니다...")
        # 이전에 저장해둔 1화 요소가 화면에서 사라질 때(stale)까지 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.staleness_of(first_ep_element_before_sort)
        )
        print("정렬 변경 완료.")

        # --- 4. 최신화 조회수 가져오기 (변경된 정렬 상태) ---
        soup_latest = BeautifulSoup(driver.page_source, 'html.parser')
        # 이제 맨 위에는 최신화가 있습니다.
        latest_ep_views = int(soup_latest.select_one("#episode_list div.ep_style2 span.episode_count_view").text.replace(',', ''))
        print(f"✅ 최신화 조회수 (최신화부터 정렬): {latest_ep_views}")

        return { "ep1_views": ep1_views, "latest_ep_views": latest_ep_views }

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return None
    finally:
        if driver:
            driver.quit()

# --- 스크립트 실행 ---
if __name__ == "__main__":
    stats = get_novel_stats()
    if stats:
        print("\n" + "="*30)
        print("🎉 최종 조회수 집계 완료! 🎉")
        print(f"1화 총 유입: {stats['ep1_views']}")
        print(f"최신화 조회수: {stats['latest_ep_views']}")
        print("="*30)