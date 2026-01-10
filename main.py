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
    # 뉴스픽 '사건사고' 섹션 - 최신 구조 반영
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 기사 리스트를 찾는 더 유연한 방법
    items = soup.find_all('p', class_='title')
    if not items:
        # 다른 태그 구조인 경우 대비
        items = soup.select('.section_list .title')
    
    if items:
        title = items[0].get_text().strip()
        # 해당 타이틀의 부모 태그에서 nid 추출
        parent_a = items[0].find_parent('a')
        if parent_a and 'nid=' in parent_a['href']:
            nid = parent_a['href'].split('nid=')[1].split('&')[0]
            return title, nid
            
    raise Exception("뉴스 기사 구조를 읽어오지 못했습니다. (선택자 재확인 필요)")

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
    print(f"✅ 카톡 전송 결과: {res.json()}")

# 실행 로직
try:
    access_token = get_kakao_token()
    if access_token:
        print("✅ 카카오 토큰 발급 완료.")
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
    print(f"⚠️ 오류 발생: {e}")
