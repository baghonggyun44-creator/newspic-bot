import requests
import json
import os
import random

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

def get_kakao_token():
    # 파일이 없으면 새 인가 코드로 토큰 생성
    if not os.path.exists(TOKEN_FILE):
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
    
    # 파일이 있으면 갱신
    with open(TOKEN_FILE, "r") as fp: tokens = json.load(fp)
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
        print("❌ 토큰 오류! 새 인가 코드를 넣어주세요.")
        return

    # 개별 기사 연결용 NID
    nid = random.choice(["8761500", "8762100", "8763000", "8759900"])
    article_url = f"https://im.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [테스트] 개별 기사 연결 확인",
            "description": "클릭 시 기사 페이지가 열리는지 보세요!",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        }
    }

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers={"Authorization": f"Bearer {token}"}, 
                        data={"template_object": json.dumps(template)})
    print(f"📢 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
