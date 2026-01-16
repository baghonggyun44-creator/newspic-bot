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
            with open(TOKEN_FILE, "w") as fp:
                json.dump(tokens, fp)
            return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰 오류! 다시 세팅이 필요할 수 있습니다.")
        return

    # [RSS 방식 조합 핵심] 뉴스픽 RSS 시스템이 선호하는 기사 구조를 사용합니다.
    # 메인으로 튕기는 현상을 방지하기 위해 cp=kakao 외에 RSS 전용 파라미터를 추가합니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # RSS 배포 기사처럼 보이기 위해 특정 리다이렉트 방지 인자(mode=rss_view)를 조합합니다.
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=rss_view&utm_medium=affiliate"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [RSS 핫이슈] 지금 난리난 뉴스 확인하기",
            "description": "뉴스픽 RSS 피드를 통해 제공되는 실시간 상세 뉴스입니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 상세 보기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    # '나에게 보내기' 실행
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"template_object": json.dumps(template)}
    
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 RSS 조합 개별 연결 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
