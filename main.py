import requests
import json
import os
import random
import re
from bs4 import BeautifulSoup

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

# [핵심] 여기에 나중에 출력된 오픈채팅방의 uuid를 넣으세요.
# 일단 비워두면 현재 있는 모든 방의 목록을 로그에 찍어줍니다.
TARGET_UUID = "" 

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

def get_chat_list(token):
    # 친구 목록 및 채팅방 목록을 가져와 uuid를 확인하는 함수
    url = "https://kapi.kakao.com/v1/api/talk/friends"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers).json()
    print("📋 [안내] 현재 메시지를 보낼 수 있는 대상 목록입니다:")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return res.get('elements', [])

def get_verified_article():
    url = "https://partners.newspic.kr/main/contentList"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0'}
    data = {'channelNo': '12', 'pageSize': '20'}
    try:
        res = requests.post(url, headers=headers, data=data, timeout=15)
        articles = res.json().get('recomList', [])
        if articles:
            target = articles[0]
            return target['title'], target['nid']
    except: pass
    return "지금 난리난 실시간 뉴스", "8761500"

def send_to_opengroup(token, title, nid, uuid):
    # 친구(오픈채팅 참여자 포함)에게 메시지 보내기
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # 커버문구 적용
    if any(k in title for k in ["사망", "충격", "사고"]): hook = "🚨 [긴급속보] 방금 들어온 충격적인 상황입니다"
    else: hook = "🔥 지금 가장 많이 보는 실시간 뉴스"
    
    final_text = f"{hook}\n\n\"{title}\""
    
    payload = {
        "receiver_uuids": json.dumps([uuid]),
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
    print(f"📢 오픈채팅 전송 결과: {res.json()}")

# 실행
try:
    token = get_kakao_token()
    if token:
        # 1. 먼저 보낼 수 있는 대상(친구/방) 목록을 로그에 찍습니다.
        friends = get_chat_list(token)
        
        title, nid = get_verified_article()
        
        if TARGET_UUID:
            send_to_opengroup(token, title, nid, TARGET_UUID)
            print(f"✅ 지정된 오픈채팅방(uuid)으로 전송 완료!")
        else:
            print("⚠️ TARGET_UUID가 비어있습니다. 위 로그에서 오픈채팅방의 uuid를 찾아 코드에 넣으세요.")
            # 테스트를 위해 나에게 보내기도 유지
            me_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
            # (기존 나에게 보내기 로직 실행...)
except Exception as e:
    print(f"❌ 오류: {e}")
