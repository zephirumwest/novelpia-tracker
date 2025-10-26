# debug.py

import requests

URL = "https://novelpia.com/novel/370230"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

print("노벨피아에 접속해서 HTML을 가져옵니다...")

try:
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    
    # requests가 받아온 순수한 HTML 텍스트를 파일로 저장합니다.
    with open("novelpia_source.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("✅ 성공! 'novelpia_source.html' 파일이 생성되었습니다.")
    print("프로젝트 폴더에서 이 파일을 웹 브라우저로 열어서 내용을 확인해보세요.")

except Exception as e:
    print(f"❌ 오류 발생: {e}")