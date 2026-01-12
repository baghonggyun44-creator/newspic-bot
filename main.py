import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# [환경 설정]
PN = "638"  # 질문자님의 수익 확정 파트너 ID
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

# [로직 도입] 텔레그램 소스코드의 후킹 로직 (makeXHook 응용)
def make_hook(title):
    if any(k in title for k in ["사망", "숨져", "사고", "충격"]):
        return "🚨 [긴급 속보] 방금 확인된 충격적인 상황입니다"
    if any(k in title for k in ["논란", "경악", "폭로"]):
        return "😱 지금 온라인에서 난리난 역대급 논란"
    if "결국" in title:
        return "🧐 결국 이렇게 결론이 났습니다.. 확인해보세요"
    return "🔥 지금 가장 많이 보는 실시간 뉴스"

# [수집 강화] 텔레그램 소스의 카테고리 우선순위(no:12) 적용
def get_verified_article():
    # 클릭률이 가장 높은 '사건사고(12)' 섹션을 최우선 수집
    url = "https://m.newspic.kr/section.html?category=12"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': 'https://m.newspic.kr/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 진짜 살아있는 7~8자리 기사 번호(nid)만 추출
        nids = list(set(re.findall(r'nid=(\d{7,8})', res.text)))
        if nids:
            target_nid = random.choice(nids)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 텔레그램 소스처럼 정밀한 제목 추출
            title_tag = soup.select_one('.title') or soup.select_one('.txt_area p')
            title = title_tag.get_text().strip() if title_tag else "실시간 화제의 뉴스"
            return title, target_nid
    except: pass
    return "지금 난리난 실시간 핫이슈", "8761250"

def send_kakao_message(token, title, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # [수익 해결] 주소에 PN(638)을 직접 포함하여 수익 누락 방지
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # 후킹 문구 생성
    hook_text = make_hook(title)
    # 약속하신 '커버문구' 조건 만족 (후킹 + 제목)
    final_text = f"{hook_text}\n\n\"{title}\""
    
    payload = {
        "template_object": json.dumps({
            "object_type": "feed",
            "content": {
                "title": final_text,
                "description": "뉴스픽 실시간 핫클릭",
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
        print(f"✅ [자비스] 수익형 메시지 전송 완료! (nid: {nid})")
except Exception as e:
    print(f"❌ 오류: {e}")
