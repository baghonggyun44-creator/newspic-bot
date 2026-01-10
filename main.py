import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 설정값
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
    # Secrets에 등록된 인가 코드로 토큰 발급 시도
    code = os.environ.get('KAKAO_CODE')
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    res = requests.post(url, data=data).json()
    if 'access_token' in res:
        print("✅ 카카오 토큰 발급 성공!")
        return res['access_token']
    else:
        print(f"❌ 토큰 발급 실패: {res}")
        return None

def get_newspic_news():
    # 뉴스픽 '사건사고' 섹션 수집 (로직 보강)
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 여러 구조에 대응할 수 있도록 선택자 수정
    items = soup.find_all('li')
    for item in items:
        link_tag = item.find('a', href=True)
        title_tag = item.find('p', class_='title') or item.find('strong')
        
        if link_tag and title_tag and 'nid=' in link_tag['href']:
            title = title_tag.get_text().strip()
            nid = link_tag['href'].split('nid=')[1].split('&')[0]
            return title, nid
    
    raise Exception("기사 정보를 찾을 수 없습니다. 뉴스픽 페이지 구조를 확인하세요.")

def send_kakao_message(token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://m.newspic.kr"},
            "button_title": "내용 확인하기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"카톡 전송 결과: {res.json()}")

# 실행
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_newspic_news()
        
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\"",
            f"📢 속보! 이건 정말 예상 밖의 일이네요...\n\n\"{title}\""
        ]
        selected_text = random.choice(covers)
        final_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        message = f"{selected_text}\n\n👇 실시간 내용 확인\n{final_url}"
        
        send_kakao_message(access_token, message)
except Exception as e:
    print(f"오류 발생: {e}")
