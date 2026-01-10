import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 사용자 설정 (정확히 입력 필수)
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
# 카카오 로그인 > 보안 메뉴에서 확인한 Client Secret을 여기에 넣으세요. 
# 만약 보안 기능을 껐다면 빈칸("")으로 두셔도 됩니다.
CLIENT_SECRET = "발급받은_보안키를_여기에_붙여넣으세요" 

def get_kakao_token():
    code = os.environ.get('KAKAO_CODE')
    if not code:
        print("❌ KAKAO_CODE가 비어있습니다. 새로 발급받아 Secrets에 저장하세요.")
        return None

    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    
    # KOE010 방지를 위해 client_secret을 포함한 데이터 구성
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code.strip(),
        "client_secret": CLIENT_SECRET # 보안키 추가
    }
    
    res = requests.post(url, headers=headers, data=data).json()
    
    if 'access_token' in res:
        print("✅ 드디어 성공! 카카오 토큰 발급 완료.")
        return res['access_token']
    else:
        print(f"❌ 토큰 발급 실패 원인: {res}")
        return None

def get_newspic_news():
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 뉴스픽 리스트 아이템 구조에 맞춘 정밀 수집
    item = soup.find('li')
    if not item or not item.find('a'):
        raise Exception("뉴스 기사 구조를 읽어오지 못했습니다.")
        
    title = item.find('p', class_='title').get_text().strip()
    link = item.find('a')['href']
    nid = link.split('nid=')[1].split('&')[0]
    return title, nid

def send_kakao_message(token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://m.newspic.kr"},
            "button_title": "기사 읽어보기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"전송 완료! 결과: {res.json()}")

# 실행 로직
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_newspic_news()
        
        # 사건사고 맞춤형 커버문구
        covers = [
            f"🚨 [긴급속보] 방금 들어온 충격적인 소식입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건 현장 상황입니다. 확인해 보세요.\n\n\"{title}\"",
            f"📢 속보! 이건 정말 예상 밖의 전개네요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 확인하기\nhttps://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        
        send_kakao_message(access_token, message)
except Exception as e:
    print(f"⚠️ 최종 실행 중 오류 발생: {e}")
