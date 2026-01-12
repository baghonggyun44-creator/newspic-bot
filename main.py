import requests
import json
import os
import random

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

# 여기에 나중에 찾은 uuid를 넣으세요. 
# 지금은 비워두면 내 정보를 로그에 찍어줍니다.
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

def get_my_info(token):
    # [수정됨] 친구 목록 대신 내 정보를 가져와서 ID를 확인합니다.
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers).json()
    print("📋 [내 정보 확인] - 아래 내용을 확인하세요:")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return res

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
    return "지금 가장 핫한 실시간 뉴스", "8761500"

def send_message(token, title, nid, uuid=None):
    article_url = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # 커버문구 적용 (수익 극대화용)
    hook = "🔥 지금 난리난 실시간 핫이슈!"
    final_text = f"{hook}\n\n\"{title}\""
    
    template = {
        "object_type": "feed",
        "content": {
            "title": final_text,
            "description": "상세한 내용은 아래 버튼을 눌러 확인하세요.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    if uuid:
        # 특정 대상(오픈채팅방 등)에게 전송
        url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        payload = {"receiver_uuids": json.dumps([uuid]), "template_object": json.dumps(template)}
    else:
        # 나에게 전송 (테스트용)
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        payload = {"template_object": json.dumps(template)}
    
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 전송 결과: {res.json()}")

# 메인 실행부
try:
    token = get_kakao_token()
    if token:
        # 내 정보를 로그에 출력합니다.
        my_info = get_my_info(token)
        
        title, nid = get_verified_article()
        
        if TARGET_UUID:
            send_message(token, title, nid, TARGET_UUID)
        else:
            print("⚠️ TARGET_UUID가 없습니다. 일단 '나에게 보내기'로 테스트합니다.")
            send_message(token, title, nid)
except Exception as e:
    print(f"❌ 오류 발생: {e}")
