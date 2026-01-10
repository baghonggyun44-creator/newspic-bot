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
    # 뉴스픽 '사건사고' 섹션 - 더 강력한 수집 로직
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 1순위: 리스트 내 타이틀 찾기
    titles = soup.select('.section_list .title') or soup.find_all('p', class_='title')
    
    for t in titles:
        parent_a = t.find_parent('a')
        if parent_a and 'nid=' in parent_a['href']:
            title = t.get_text().strip()
            nid = parent_a['href'].split('nid=')[1].split('&')[0]
            return title, nid
            
    # 2순위: 모든 <a> 태그 중 nid가 포함된 첫 번째 링크 찾기
    for a in soup.find_all('a', href=True):
        if 'nid=' in a['href']:
            nid = a['href'].split('nid=')[1].split('&')[0]
            title = a.get_text().strip() or "최신 사건사고 뉴스"
            return title, nid
            
    raise Exception("뉴스 기사 구조를 읽어오지 못했습니다.")

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

# 실행
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_newspic_news()
        covers = [
            f"🚨 [긴급] 방금 들어온 충격적인 소식입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건 현장 상황!\n\n\"{title}\"",
            f"📢 속보! 이건 정말 조심해야겠네요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인\nhttps://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        send_kakao_message(access_token, message)
except Exception as e:
    print(f"⚠️ 오류: {e}")
