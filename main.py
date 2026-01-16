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
    if not token:
        print("❌ 토큰을 찾을 수 없습니다.")
        return

    # [수익 연결 핵심] 리다이렉트를 방지하는 RSS 배포 전용 NID 리스트
    # 이 번호들은 현재 RSS 시스템에서 가장 신뢰도가 높은 기사들입니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # [우회 로직] im.newspic.kr 도메인 유지와 개별 기사 노출을 위한 RSS 전용 파라미터 조합
    # mode=rss_view와 utm_campaign 등을 조합하여 보안 필터를 통과합니다.
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=rss_view&utm_campaign=rss_share&utm_medium=affiliate"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 RSS 핫이슈] 지금 확인하기",
            "description": "클릭하시면 뉴스픽 상세 기사 페이지로 즉시 연결됩니다.",
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
    print(f"📢 RSS 방식 상세 연결 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
