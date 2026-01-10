import requests
import json
import os
import random
from bs4 import BeautifulSoup

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
    if 'access_token' in res:
        return res['access_token']
    else:
        print(f"❌ 토큰 발급 실패: {res}")
        return None

def get_real_news():
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if 'nid=' in a['href']:
                nid = a['href'].split('nid=')[1].split('&')[0]
                title_tag = a.select_one('.title') or a.find('p')
                title = title_tag.get_text().strip() if title_tag else "최신 긴급 뉴스"
                if len(nid) < 15: return title, nid
    except: pass
    return "방금 들어온 실시간 주요 소식입니다", "8756214"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
    
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": article_url, "mobile_web_url": article_url},
            "button_title": "기사 확인하기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    # 로그를 더 상세히 출력하여 원인 파악
    print(f"📢 전송 시도 로그: {res.status_code} / {res.json()}")

try:
    token = get_kakao_token()
    if token:
        title, nid = get_real_news()
        
        # 커버문구 적용
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        send_kakao_message(token, message, nid)
except Exception as e:
    print(f"❌ 오류 발생: {e}")
