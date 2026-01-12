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
    # 보안 우회를 위한 실제 브라우저 위장 데이터
    url = "https://m.newspic.kr/section.html?category=TOTAL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 진짜 살아있는 7~8자리 기사 번호만 추출
        nids = list(set(re.findall(r'nid=(\d{7,8})', res.text)))
        if nids:
            # 뉴스픽의 추적을 피하기 위해 리스트에서 랜덤하게 선택
            target_nid = random.choice(nids)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = "방금 들어온 실시간 핫이슈"
            title_tag = soup.select_one('.title') or soup.find('p')
            if title_tag:
                title = title_tag.get_text().strip()
            return title, target_nid
    except:
        pass
    # 모든 수집 실패 시, 현재 뉴스픽 메인에 떠 있는 확실한 번호 (테스트용)
    return "방금 들어온 충격적인 긴급 소식", "8761400"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [최종 우회 로직] 뉴스픽이 신뢰하는 카카오 유입 신호(cp=kakao)와 랜덤 인증값 부여
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    payload = {
        "template_object": json.dumps({
            "object_type": "feed",
            "content": {
                "title": text,
                "description": "지금 확인해야 할 실시간 뉴스",
                "image_url": "https://m.newspic.kr/images/common/og_logo.png",
                "link": {"web_url": article_url, "mobile_web_url": article_url}
            },
            "buttons": [{"title": "기사 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
        })
    }
    requests.post(url, headers=headers, data=payload)

# 메인 실행부
try:
    token = get_kakao_token()
    if token:
        title, nid = get_real_article()
        
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 화제의 현장! 확인해 보세요.\n\n\"{title}\""
        ]
        message = random.choice(covers)
        
        send_kakao_message(token, message, nid)
        print(f"✅ 기사 전송 완료! (최종 활성 nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
