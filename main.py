import requests
import json
import os
import random
import re
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
    if not tokens:
        code = os.environ.get('KAKAO_CODE')
        if not code: return None
        url = "https://kauth.kakao.com/oauth/token"
        data = {"grant_type": "authorization_code", "client_id": REST_API_KEY, "redirect_uri": REDIRECT_URI, "code": code.strip()}
        res = requests.post(url, data=data).json()
        if 'access_token' in res:
            save_tokens(res)
            return res['access_token']
        return None
    url = "https://kauth.kakao.com/oauth/token"
    data = {"grant_type": "refresh_token", "client_id": REST_API_KEY, "refresh_token": tokens['refresh_token']}
    res = requests.post(url, data=data).json()
    if 'access_token' in res:
        tokens['access_token'] = res['access_token']
        if 'refresh_token' in res: tokens['refresh_token'] = res['refresh_token']
        save_tokens(tokens)
        return tokens['access_token']
    return None

def get_real_article():
    # 뉴스픽 메인에서 진짜 뉴스 번호를 낚아챕니다.
    url = "https://m.newspic.kr/"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            # 중요: nid= 뒤의 7~8자리 숫자만 골라내고 긴 날짜형태는 무시합니다.
            match = re.search(r'nid=(\d{7,8})', href)
            if match:
                nid = match.group(1)
                title_tag = a.select_one('.title') or a.select_one('p')
                title = title_tag.get_text().strip() if title_tag else "최신 화제 뉴스"
                return title, nid
    except: pass
    # 수집 실패 시 실제 작동하는 번호로 연결 (테스트용)
    return "방금 올라온 긴급 실시간 소식", "8758412"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    # 추출된 진짜 숫자 nid를 사용하여 최종 수익 링크 생성
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

# 실행 로직
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_real_article()
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 화제의 현장! 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        send_kakao_message(access_token, message, nid)
        print(f"✅ 전송 완료 (nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
