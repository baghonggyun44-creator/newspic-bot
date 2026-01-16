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
    # 기존에 저장된 토큰을 불러와서 갱신합니다.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp:
            tokens = json.load(fp)
        
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": REST_API_KEY,
            "refresh_token": tokens['refresh_token']
        }
        res = requests.post(url, data=data).json()
        
        if 'access_token' in res:
            tokens['access_token'] = res['access_token']
            if 'refresh_token' in res:
                tokens['refresh_token'] = res['refresh_token']
            with open(TOKEN_FILE, "w") as fp:
                json.dump(tokens, fp)
            return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰을 갱신할 수 없습니다. 인가 코드를 새로 입력하여 토큰을 생성하세요.")
        return

    # [수익 링크] 뉴스픽 메인 페이지 이동 방지를 위한 기사 번호 조합
    # 질문자님의 도메인 im.newspic.kr을 사용합니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao"
    
    # 메시지 구성
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 지금 확인해보세요!",
            "description": "클릭하시면 뉴스픽 기사 페이지로 이동합니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 바로 읽기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    # '나에게 보내기' API 호출
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"template_object": json.dumps(template)}
    
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 전송 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
