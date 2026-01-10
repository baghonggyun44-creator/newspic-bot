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
    # GitHub Secrets에서 새로 받은 인가 코드를 가져옴
    code = os.environ.get('KAKAO_CODE')
    if not code:
        print("❌ KAKAO_CODE가 없습니다. 새로 발급받아 Secrets에 넣어주세요.")
        return None

    url = "https://kauth.kakao.com/oauth/token"
    # 헤더와 데이터를 카카오 표준 규격에 맞게 설정 (KOE010 방지)
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "authorization_code",
        "client_id": REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": code.strip()
    }
    
    res = requests.post(url, headers=headers, data=data).json()
    
    if 'access_token' in res:
        print("✅ 카카오 토큰 발급에 성공했습니다!")
        return res['access_token']
    else:
        # 에러 발생 시 상세 이유 출력
        print(f"❌ 토큰 발급 실패 상세: {res}")
        return None

def get_newspic_news():
    # 뉴스픽 '사건사고' 섹션 수집
    url = "https://m.newspic.kr/section.html?category=%EC%82%AC%EA%B1%B4%EC%82%AC%EA%B3%A0"
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 기사 제목과 ID 추출
    item = soup.select_one('ul.section_list li')
    if not item:
        raise Exception("기사 리스트를 찾을 수 없습니다.")
        
    title = item.select_one('.title').get_text().strip()
    link = item.find('a', href=True)['href']
    nid = link.split('nid=')[1].split('&')[0]
    return title, nid

def send_kakao_message(token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": text,
            "link": {"web_url": "https://m.newspic.kr"},
            "button_title": "내용 확인하기"
        })
    }
    res = requests.post(url, headers=headers, data=payload)
    print(f"카톡 전송 결과: {res.json()}")

# 실행 부분
try:
    access_token = get_kakao_token()
    if access_token:
        title, nid = get_newspic_news()
        
        # 커버문구 랜덤 선택
        covers = [
            f"🚨 [긴급 소식] 방금 들어온 충격적인 상황입니다.\n\n\"{title}\"",
            f"⚠️ 지금 난리 난 사건사고 현장입니다. 확인해 보세요.\n\n\"{title}\"",
            f"📢 속보! 이건 정말 예상 밖의 일이네요...\n\n\"{title}\""
        ]
        selected_text = random.choice(covers)
        final_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}"
        message = f"{selected_text}\n\n👇 실시간 상황 바로 확인\n{final_url}"
        
        send_kakao_message(access_token, message)
except Exception as e:
    print(f"최종 에러 발생: {e}")
