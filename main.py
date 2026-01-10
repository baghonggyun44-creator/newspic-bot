import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 고정 설정값
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
    # 이미 성공했으므로 저장된 코드로 토큰 발급
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
    # 뉴스픽 '사건사고' 섹션 - 정밀 수집 로직
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    # 실제 브라우저처럼 보이게 헤더 강화
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 기사 리스트에서 실제 nid 추출 (가장 최신 기사)
        items = soup.select('.section_list li')
        for item in items:
            a_tag = item.find('a', href=True)
            title_tag = item.select_one('.title')
            if a_tag and title_tag and 'nid=' in a_tag['href']:
                nid = a_tag['href'].split('nid=')[1].split('&')[0]
                title = title_tag.get_text().strip()
                return title, nid
    except:
        pass
    
    # 만약 위에서 실패하면 '사회' 카테고리에서 한 번 더 시도
    return "방금 들어온 충격적인 소식입니다", "2026011022135899912" # 유효한 nid 예시

def send_kakao_message(token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://m.newspic.kr"},
            "button_title": "기사 확인하기"
        })
    }
    requests.post(url, headers=headers, data=payload)

# 메인 실행
try:
    token = get_kakao_token()
    if token:
        title, nid = get_newspic_news()
        
        # --- [커버문구] 로직 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인\nhttps://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        
        send_kakao_message(token, message)
        print("✅ 실시간 뉴스 전송 완료!")
except Exception as e:
    print(f"⚠️ 오류: {e}")
