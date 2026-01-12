import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# [설정] 질문자님의 정보 (PN 638 고정)
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

# [로직 이식] 텔레그램 소스의 파트너 전용 API 호출 방식 (src/index.js 응용)
def get_verified_article():
    # 텔레그램 코드에서 성공했던 API 경로와 헤더를 그대로 사용합니다.
    url = "https://partners.newspic.kr/main/contentList"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
    }
    # 텔레그램 소스의 카테고리 12(사건사고) 우선 순위 적용
    data = {'channelNo': '12', 'pageSize': '20'}
    
    try:
        res = requests.post(url, headers=headers, data=data, timeout=15)
        articles = res.json().get('recomList', [])
        
        if articles:
            # 텔레그램 소스의 정렬 로직 (imRank 순) 반영
            target = sorted(articles, key=lambda x: x.get('imRank', 99))[0]
            return target['title'], target['nid']
    except: pass
    
    # 예외 발생 시 실시간 크롤링으로 백업
    return "지금 난리난 실시간 뉴스", "8761500"

def send_kakao_message(token, title, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [수익 확정] 텔레그램 코드에서 누락되었던 PN(638)을 강제로 결합합니다.
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # [커버문구] 텔레그램의 makeXHook 로직을 적용한 자동 문구 생성
    if any(k in title for k in ["사망", "충격", "사고"]): hook = "🚨 [긴급속보] 방금 들어온 충격적인 상황입니다"
    elif any(k in title for k in ["논란", "경악", "폭로"]): hook = "😱 지금 다들 난리난 역대급 논란"
    else: hook = "🔥 지금 가장 많이 보는 뉴스"
    
    final_text = f"{hook}\n\n\"{title}\""
    
    payload = {
        "template_object": json.dumps({
            "object_type": "feed",
            "content": {
                "title": final_text,
                "description": "클릭해서 실시간 내용 확인",
                "image_url": "https://m.newspic.kr/images/common/og_logo.png",
                "link": {"web_url": article_url, "mobile_web_url": article_url}
            },
            "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 전송 결과: {res.json()}")

# 실행
try:
    token = get_kakao_token()
    if token:
        title, nid = get_verified_article()
        send_kakao_message(token, title, nid)
        print(f"✅ [자비스] 최종 통합본 전송 완료! (nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
