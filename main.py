import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 설정값 (질문자님 전용)
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
    # 이미 발급 성공했으므로 Secrets에서 가져옴
    code = os.environ.get('KAKAO_CODE')
    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code.strip()
    }
    res = requests.post(url, headers=headers, data=data).json()
    return res.get('access_token')

def get_newspic_news():
    # 뉴스픽 '사건사고' 섹션 수집 - 최신 구조 정밀 타겟팅
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 기사 리스트에서 첫 번째 기사 찾기
    item = soup.select_one('.section_list li')
    if not item:
        # 대안 구조 확인
        item = soup.find('li')
    
    if item:
        title_tag = item.select_one('.title') or item.find('p')
        link_tag = item.find('a', href=True)
        
        if title_tag and link_tag:
            title = title_tag.get_text().strip()
            nid = link_tag['href'].split('nid=')[1].split('&')[0]
            return title, nid
            
    raise Exception("뉴스 기사 구조를 읽어오지 못했습니다. 뉴스픽 페이지를 확인하세요.")

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
    print(f"✅ 카톡 전송 시도 결과: {res.json()}")

# 실행 로직
try:
    access_token = get_kakao_token()
    if access_token:
        print("✅ 카카오 토큰 인증 성공.")
        title, nid = get_newspic_news()
        
        # --- [커버문구 로직 적용] ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\"",
            f"📢 속보! 이건 정말 예상 밖의 일이네요...\n\n\"{title}\""
        ]
        selected_text = random.choice(covers)
        final_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        message = f"{selected_text}\n\n👇 실시간 내용 확인\n{final_url}"
        
        send_kakao_message(access_token, message)
    else:
        print("❌ 토큰을 가져오지 못했습니다. 인가 코드를 갱신해 주세요.")
except Exception as e:
    print(f"⚠️ 실행 중 오류 발생: {e}")
