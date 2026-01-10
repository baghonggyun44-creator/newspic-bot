import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 고정 설정값
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as fp:
        json.dump(tokens, fp)

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp:
            return json.load(fp)
    return None

def get_kakao_token():
    tokens = load_tokens()
    
    # [처음 실행 시] 인가 코드로 첫 토큰 발급
    if not tokens:
        code = os.environ.get('KAKAO_CODE')
        if not code: return None
        
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code.strip()
        }
        res = requests.post(url, data=data).json()
        if 'access_token' in res:
            save_tokens(res)
            return res['access_token']
        return None

    # [두 번째부터] 리프레시 토큰으로 자동 갱신
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": REST_API_KEY,
        "refresh_token": tokens['refresh_token']
    }
    res = requests.post(url, data=data).json()
    
    if 'access_token' in res:
        tokens['access_token'] = res['access_token']
        if 'refresh_token' in res: # 리프레시 토큰도 갱신될 경우 업데이트
            tokens['refresh_token'] = res['refresh_token']
        save_tokens(tokens)
        return tokens['access_token']
    return None

def get_real_article():
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if 'nid=' in a['href']:
                nid = a['href'].split('nid=')[1].split('&')[0]
                if len(nid) < 15:
                    title_tag = a.select_one('.title') or a.find('p')
                    title = title_tag.get_text().strip() if title_tag else "최신 사건사고"
                    return title, nid
    except: pass
    return "방금 들어온 실시간 주요 소식", "8756214"

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
    requests.post(url, headers=headers, data=payload)

# 메인 실행
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_real_article()
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        send_kakao_message(access_token, message, nid)
        print("✅ 자동 갱신 및 전송 완료!")
except Exception as e:
    print(f"❌ 오류: {e}")
