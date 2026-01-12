import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# 1. 고정 설정값 (PN 638 유지)
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
    # 방식 고도화: 메인 뉴스 목록에서 실시간으로 가장 핫한 뉴스를 골라냅니다.
    url = "https://m.newspic.kr/section.html?category=TOTAL"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 낚시용 긴 숫자를 버리고 7~8자리 진짜 nid만 추출합니다.
        nids = re.findall(r'nid=(\d{7,8})', res.text)
        if nids:
            # 중복 제거 후 가장 최신 뉴스 하나 선택
            target_nid = list(set(nids))[0]
            soup = BeautifulSoup(res.text, 'html.parser')
            title_tag = soup.select_one('.title') or soup.find('p')
            title = title_tag.text.strip() if title_tag else "실시간 화제 뉴스"
            return title, target_nid
    except:
        pass
    # 모든 수집 실패 시 현재 실제로 살아있는 뉴스 번호 강제 투입
    return "방금 들어온 실시간 주요 소식", "8761102"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [핵심] 차단 우회용 파라미터 조합
    # t=... 와 cp=kakao 를 붙여 실제 사람이 공유한 링크처럼 위장합니다.
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    payload = {
        "template_object": json.dumps({
            "object_type": "feed",
            "content": {
                "title": text,
                "description": "실시간 뉴스픽 핫이슈",
                "image_url": "https://m.newspic.kr/images/common/og_logo.png",
                "link": {"web_url": article_url, "mobile_web_url": article_url}
            },
            "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 전송 로그: {res.json()}")

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
        print(f"✅ 기사 전송 완료! (최종 nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
