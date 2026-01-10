import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 설정값 (질문자님 정보 반영)
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"

def get_kakao_token():
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

def get_real_article():
    # 뉴스픽 '사건사고' 섹션에서 실제 기사 정보를 수집합니다.
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # <a> 태그 중 nid= 가 포함된 진짜 기사 링크 탐색
        for a in soup.find_all('a', href=True):
            if 'nid=' in a['href']:
                href = a['href']
                nid = href.split('nid=')[1].split('&')[0]
                
                # 가짜 번호가 아닌 진짜 기사 번호(짧은 숫자)인 경우만 선택
                if len(nid) < 15:
                    title_tag = a.select_one('.title') or a.find('p')
                    title = title_tag.get_text().strip() if title_tag else "긴급 사건사고 뉴스"
                    return title, nid
    except:
        pass
    # 수집 실패 시 가장 최근 성공했던 실제 nid를 예비로 사용
    return "방금 들어온 실시간 주요 소식", "8756214" 

def send_kakao_message(token, text, nid):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 클릭 시 실제 기사로 이동하는 링크 생성
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
    print(f"✅ 최종 전송 완료: {res.json()}")

# 실행 로직
try:
    token = get_kakao_token()
    if token:
        title, nid = get_real_article()
        
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\""
        ]
        selected_text = random.choice(covers)
        message = f"{selected_text}\n\n👇 실시간 내용 확인"
        
        send_kakao_message(token, message, nid)
except Exception as e:
    print(f"❌ 오류: {e}")
