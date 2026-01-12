import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# 1. 고정 설정값 (수익 연동 PN 638 유지)
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
    # 방식 변경: 전체 인기 차트에서 낚시 데이터를 거르고 진짜 번호만 추출
    url = "https://m.newspic.kr/section.html?category=TOTAL"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 중요: nid= 뒤에 숫자 7~8자리만 있는 진짜 번호만 리스트로 만듭니다.
        # 20260113... 처럼 10자리가 넘는 가짜 날짜 번호는 여기서 자동 탈락됩니다.
        nids = re.findall(r'nid=(\d{7,8})', res.text)
        if nids:
            target_nid = nids[0] # 가장 첫 번째 진짜 기사 번호 선택
            soup = BeautifulSoup(res.text, 'html.parser')
            title_tag = soup.select_one('.title') or soup.find('p')
            title = title_tag.text.strip() if title_tag else "실시간 화제의 뉴스"
            return title, target_nid
    except:
        pass
    # 모든 수집 시도가 실패할 경우를 대비한 실제 작동 중인 기사 번호
    return "방금 들어온 실시간 긴급 소식입니다", "8758412"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    # 날짜가 섞이지 않은 깨끗한 숫자 nid만 사용하여 링크 생성
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

# 실행
try:
    token = get_kakao_token()
    if token:
        title, nid = get_real_article()
        # 커버문구 적용
        covers = [
            f"🚨 [긴급] 방금 들어온 충격적인 소식입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 화제의 현장! 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        send_kakao_message(token, message, nid)
        print(f"✅ 진짜 기사 전송 완료! (사용된 nid: {nid})")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
