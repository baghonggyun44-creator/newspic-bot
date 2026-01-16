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
        data = {"grant_type": "refresh_token", "client_id": REST_API_KEY, "refresh_token": tokens['refresh_token']}
        res = requests.post(url, data=data).json()
        if 'access_token' in res:
            tokens['access_token'] = res['access_token']
            with open(TOKEN_FILE, "w") as fp: json.dump(tokens, fp)
            return res['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token: return

    # [수익 연결 핵심] 리다이렉트를 방어하는 검증된 기사 번호
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # [우회 로직] 뉴스픽 보안 필터를 통과하기 위한 다중 파라미터 조합
    # 1. mode=view_all: 리다이렉트 방지 모드
    # 2. utm 파라미터: 정상적인 SNS 유입 경로로 위장
    # 3. v=1.1: 최신 배포 버전 신호 추가
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=view_all&v=1.1&utm_source=kakao&utm_medium=sns&utm_campaign=share"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 개별 기사 확인하기",
            "description": "클릭하시면 뉴스픽 상세 기사 페이지로 즉시 이동합니다.",
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

    # 나에게 보내기 실행
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers={"Authorization": f"Bearer {token}"}, 
                        data={"template_object": json.dumps(template)})
    print(f"📢 개별 기사 정밀 우회 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
