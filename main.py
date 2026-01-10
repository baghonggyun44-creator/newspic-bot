import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 고정 설정값
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
    # 저장된 KAKAO_CODE로 토큰을 가져옵니다.
    code = os.environ.get('KAKAO_CODE')
    url = "https://kauth.kakao.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code.strip()
    }
    res = requests.post(url, headers=headers, data=data).json()
    return res.get('access_token')

def get_real_news():
    # 뉴스픽 '사건사고' 페이지에서 실제 기사 정보를 낚아챕니다.
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # <a> 태그 중에서 nid= 가 포함된 모든 링크를 찾습니다.
        for a in soup.find_all('a', href=True):
            if 'nid=' in a['href']:
                # 실제 nid 숫자만 추출 (예: 123456)
                full_href = a['href']
                nid = full_href.split('nid=')[1].split('&')[0]
                
                # 기사 제목 추출
                title_tag = a.select_one('.title') or a.find('p')
                title = title_tag.get_text().strip() if title_tag else "최신 사건사고 뉴스"
                
                # 테스트용 가짜 번호가 아닌 진짜 번호인 경우만 반환
                if len(nid) < 15: 
                    return title, nid
    except Exception as e:
        print(f"수집 중 오류: {e}")
    
    # 만약 실패하면 가장 조회수 높은 고정 기사라도 보냅니다 (유효한 링크)
    return "방금 들어온 실시간 주요 소식입니다", "8756214"

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 실제 기사 링크 생성
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
    
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": article_url, "mobile_web_url": article_url},
            "button_title": "기사 읽어보기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"✅ 전송 결과: {res.json()}")

# 실행 부분
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_real_news()
        
        # 커버문구 적용
        covers = [
            f"🚨 [긴급] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\""
        ]
        message = f"{random.choice(covers)}\n\n👇 실시간 내용 확인"
        
        send_kakao_message(access_token, message, nid)
except Exception as e:
    print(f"❌ 최종 실행 오류: {e}")
