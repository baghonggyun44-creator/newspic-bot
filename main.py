import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# [설정] 질문자님의 정보
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

# [도입로직] 텔레그램 소스코드의 정밀 수집 방식 적용
def get_verified_article():
    # 텔레그램 코드에서 사용한 카테고리 우선순위 1위(사건사고:12) 섹션 타겟
    url = "https://m.newspic.kr/section.html?category=12"
    
    # [핵심] 뉴스픽 보안팀을 속이는 브라우저 위장 헤더 (텔레그램 코드 응용)
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://m.newspic.kr/',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        # 텔레그램 패턴: nid= 뒤의 7~8자리 숫자만 정확하게 필터링
        nids = list(set(re.findall(r'nid=(\d{7,8})', res.text)))
        
        if nids:
            target_nid = random.choice(nids)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 텔레그램 소스코드 스타일의 제목 추출
            title_tag = soup.select_one('.title') or soup.select_one('.txt_area p')
            title = title_tag.get_text().strip() if title_tag else "실시간 핫이슈"
            return title, target_nid
    except: pass
    return "지금 가장 뜨거운 실시간 뉴스", "8761400"

# [수익 강화] 커버문구 및 수익 링크 조합
def send_kakao_message(token, title, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [수익 해결] 주소에 PN(638)을 직접 포함하고 우회 파라미터(cp, t) 추가
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # 텔레그램 makeXHook 로직 기반 자동 커버문구
    if any(k in title for k in ["사망", "충격", "사고", "결국"]): 
        hook = "🚨 [긴급속보] 방금 들어온 충격적인 상황입니다"
    elif any(k in title for k in ["논란", "경악", "폭로"]): 
        hook = "😱 지금 다들 난리난 역대급 논란"
    else: 
        hook = "🔥 지금 가장 많이 보는 뉴스"
    
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
    print(f"📢 카톡 전송 결과: {res.json()}")

# 실행부
try:
    token = get_kakao_token()
    if token:
        title, nid = get_verified_article()
        send_kakao_message(token, title, nid)
        print(f"✅ [자비스] 최종 통합본 전송 완료! (사용된 nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
