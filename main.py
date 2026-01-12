import requests
import json
import os
import random

# [설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

# [중요] 로그에서 찾은 숫자 ID를 여기에 넣으세요 (예: 4689990492)
TARGET_ID = "" 

def get_kakao_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp: tokens = json.load(fp)
    else:
        code = os.environ.get('KAKAO_CODE')
        if not code: return None
        res = requests.post("https://kauth.kakao.com/oauth/token", data={
            "grant_type": "authorization_code", "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI, "code": code.strip()
        }).json()
        if 'access_token' in res:
            with open(TOKEN_FILE, "w") as fp: json.dump(res, fp)
            return res['access_token']
        return None
    
    res = requests.post("https://kauth.kakao.com/oauth/token", data={
        "grant_type": "refresh_token", "client_id": REST_API_KEY, "refresh_token": tokens['refresh_token']
    }).json()
    if 'access_token' in res:
        tokens['access_token'] = res['access_token']
        with open(TOKEN_FILE, "w") as fp: json.dump(tokens, fp)
        return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰을 가져오지 못했습니다. KAKAO_CODE를 확인하세요.")
        return

    # 내 정보 강제 출력
    me = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {token}"}).json()
    print("\n✅ [회원번호 확인]:", me.get('id'))
    print("------------------------------------------")

    # 기사 가져오기
    res = requests.post("https://partners.newspic.kr/main/contentList", data={'channelNo': '12', 'pageSize': '20'}).json()
    article = res.get('recomList', [{}])[0]
    title = article.get('title', '실시간 핫이슈')
    nid = article.get('nid', '8761500')
    link = f"https://m.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao"

    # 메시지 템플릿
    template = {
        "object_type": "feed",
        "content": {
            "title": f"🔥 {title}",
            "description": "지금 바로 확인해보세요",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": link, "mobile_web_url": link}
        },
        "buttons": [{"title": "기사 읽기", "link": {"web_url": link, "mobile_web_url": link}}]
    }

    # 전송 (나에게 보내기)
    send_res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                             headers={"Authorization": f"Bearer {token}"},
                             data={"template_object": json.dumps(template)})
    print("📢 전송 결과:", send_res.json())

if __name__ == "__main__":
    run_bot()
