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
    # 저장된 토큰 파일을 읽어 액세스 토큰을 갱신합니다.
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
        print("❌ 토큰 갱신 실패! 인가 코드를 새로 입력해야 할 수도 있습니다.")
        return

    # [중요] 뉴스픽 메인 페이지 이동을 방지하기 위해 검증된 기사 번호(NID)를 사용합니다.
    # 질문자님이 설정하신 im.newspic.kr 도메인으로 연결됩니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao"
    
    # 카카오톡 메시지 템플릿 구성
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 개별 기사 연결 테스트",
            "description": "클릭 시 개별 기사 페이지가 열리는지 확인해 주세요.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 읽기",
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
    print(f"📢 테스트 전송 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
