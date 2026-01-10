import requests
import json
import os
import random
from bs4 import BeautifulSoup

# 1. 설정값
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

def get_newspic_news():
    # 뉴스픽 '사건사고' 섹션 - 수집 로직 3단계 보강
    targets = [
        "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0",
        "https://m.newspic.kr/section.html?category=사회"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in targets:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 모든 <a> 태그 중 nid가 포함된 링크를 싹 뒤집니다
            links = soup.find_all('a', href=True)
            for a in links:
                if 'nid=' in a['href']:
                    nid = a['href'].split('nid=')[1].split('&')[0]
                    # 제목이 비어있으면 텍스트 추출, 그것도 없으면 기본 문구
                    title = a.get_text().strip() or "최신 긴급 사건사고 소식"
                    if len(title) > 5: # 너무 짧은 제목 제외
                        return title.split('\n')[0], nid
        except:
            continue
            
    # 정 안되면 최근 많이 본 뉴스 nid 하나를 강제로라도 반환 (테스트용)
    return "방금 들어온 실시간 주요 소식입니다", "20260111123456" 

def send_kakao_message(token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://m.newspic.kr"},
            "button_title": "기사 확인하기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"✅ 카톡 전송 시도 결과: {res.json()}")

# 실행
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_newspic_news()
        
        # --- 커버문구 적용 ---
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\"",
            f"📢 속보! 이건 정말 예상 밖의 일이네요...\n\n\"{title}\""
        ]
        selected_text = random.choice(covers)
        final_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        message = f"{selected_text}\n\n👇 실시간 내용 확인\n{final_url}"
        
        send_kakao_message(access_token, message)
except Exception as e:
    print(f"⚠️ 최종 오류 발생: {e}")
