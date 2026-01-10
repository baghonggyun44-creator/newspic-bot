import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 환경 설정
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
    # 최초 실행 시 Secrets의 인가코드로 토큰 발급
    code = os.environ.get('KAKAO_CODE')
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    response = requests.post(url, data=data).json()
    return response.get("access_token")

def get_newspic_news():
    # 뉴스픽 '사건사고' 카테고리 실시간 인기 기사 수집
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 상위 1개 기사만 추출 (도배 방지)
    item = soup.select_one('.section_list li')
    title = item.select_one('.title').text.strip()
    link_raw = item.select_one('a')['href']
    nid = link_raw.split('nid=')[1].split('&')[0]
    return title, nid

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
    requests.post(url, headers=headers, data=payload)

# 실행 로직
try:
    token = get_kakao_token()
    title, nid = get_newspic_news()
    
    # --- [커버문구 로직 적용] ---
    covers = [
        f"🚨 [긴급] 방금 들어온 충격적인 소식입니다.\n\n\"{title}\"",
        f"⚠️ 지금 난리 난 사건사고 현장 상황입니다.\n\n\"{title}\"",
        f"📢 속보! 이건 정말 상상도 못 했네요...\n\n\"{title}\""
    ]
    selected_text = random.choice(covers)
    final_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
    message = f"{selected_text}\n\n👇 실시간 상황 바로 확인\n{final_url}"
    
    send_kakao_message(token, message)
    print("성공적으로 전송되었습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
