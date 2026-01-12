import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# 1. 고정 설정값 (질문자님의 PN 638 유지)
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
    # 방식 변경: 실시간 인기 뉴스 목록 전체에서 랜덤하게 낚아챕니다.
    url = "https://m.newspic.kr/section.html?category=TOTAL"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 중요: 낚시용 긴 번호는 버리고, 실제 작동하는 7~8자리 숫자 nid만 골라냅니다.
        nids = list(set(re.findall(r'nid=(\d{7,8})', res.text)))
        if nids:
            # 매번 똑같은 번호를 보내지 않도록 랜덤 선택
            target_nid = random.choice(nids)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 해당 기사의 실제 제목을 찾으려 시도합니다.
            title = "방금 들어온 실시간 화제의 뉴스"
            title_tag = soup.select_one('.title') or soup.select_one('p')
            if title_tag:
                title = title_tag.get_text().strip()
            return title, target_nid
    except: pass
    # 수집 실패 시 최후의 수단: 현재 가장 핫한 기사 번호 강제 투입
    return "지금 가장 뜨거운 실시간 핫이슈", "8761250"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    # 차단 우회용 파라미터(cp, t)를 조합한 최종 수익 링크
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    payload = {
        "template_object": json.dumps({
            "object_type": "feed",
            "content": {
                "title": text,
                "description": "실시간 뉴스픽 소식",
                "image_url": "https://m.newspic.kr/images/common/og_logo.png",
                "link": {"web_url": article_url, "mobile_web_url": article_url}
            },
            "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
        })
    }
    requests.post(url, headers=headers, data=payload)

# 실행
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_real_article()
        
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 화제의 현장! 확인해 보세요.\n\n\"{title}\""
        ]
        message = random.choice(covers)
        
        send_kakao_message(access_token, message, nid)
        print(f"✅ 기사 전송 완료! (사용된 nid: {nid})")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
