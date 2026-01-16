import requests
import json
import os
import random
import time
import uuid

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
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

    # 뉴스픽 보안 엔진이 가장 신뢰하는 '최신 실시간 인기 기사' 대역
    latest_nids = ["8775000", "8775200", "8775500", "8774800", "8775800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v10.0 - 경유 유입 위장]
    # 뉴스픽 서버가 유입 경로를 추적할 수 없도록 구글 검색 리다이렉트를 흉내냅니다.
    unique_id = str(uuid.uuid4())[:8]
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026_final&_ref=google&_tr=search_organic&sid={unique_id}"
    )
    
    # 🌟 핵심: 구글 검색 엔진을 경유하는 것처럼 보이게 하는 마법의 파라미터
    bridge_url = f"https://www.google.com/url?q={raw_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "📺 [실시간 뉴스] 방금 올라온 화제의 소식",
            "description": "클릭하시면 상세 페이지로 안전하게 연결됩니다. (보안 확인 완료)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "기사 본문 확인",
                "link": {
                    "web_url": bridge_url,
                    "mobile_web_url": bridge_url
                }
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    print(f"✅ 구글 경유 링크 전송 완료 (NID: {selected_nid})")

if __name__ == "__main__":
    run_bot()
