import requests
import json
import os
import random
import re  # 이 부분이 숫자만 골라내는 핵심 도구입니다
from bs4 import BeautifulSoup

# 1. 설정값 (질문자님의 PN 638 유지)
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
    # 뉴스픽 메인 페이지에서 수집
    url = "https://m.newspic.kr/"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            # 중요: nid= 뒤의 7~8자리 숫자만 골라내고 긴 날짜형태는 버립니다
            match = re.search(r'nid=(\d{7,8})', href)
            if match:
                nid = match.group(1)
                title_tag = a.select_one('.title') or a.select_one('p')
                title = title_tag.get_text().strip() if title_tag else "최신 화제 뉴스"
                return title, nid
    except: pass
    return "방금 들어온 실시간 주요 소식", "8758412" # 실제 작동하는 백업 번호

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    # 숫자만 남은 nid로 진짜 수익 링크 생성
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
    print(f"📢 전송 결과: {res.json()}")

# 실행 부분
try:
    token = get_kakao_token()
    if token:
        title, nid = get_real_article()
        
        # 커버문구 적용
        covers = [
            f"🚨 [긴급] 방금 들어온 충격적인 소식입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장! 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        
        send_kakao_message(token, message, nid)
        print(f"✅ 최종 전송 완료! (nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
