import requests
import json
import os
import random
import time
import uuid

# [환경 설정]
PN = "616" 
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

    # PC 유입으로 인정받기 쉬운 최신 뉴스 대역
    latest_nids = ["8800100", "8800250", "8800500", "8799800", "8800800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v36.0 - PC 유입 세탁]
    unique_id = str(uuid.uuid4())[:8]
    # 실제 PC에서 공유했을 때 붙는 파라미터 구조를 흉내냅니다.
    target_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=pc_stable&sid={unique_id}"
    )
    
    # 구글 공식 리다이렉트 (PC 브라우저가 가장 신뢰하는 경로)
    bridge_url = f"https://www.google.com/url?q={target_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [실시간] PC에서도 화제인 오늘 뉴스",
            "description": "상세 기사로 즉시 연결됩니다. (공식 보안 통과)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "원문 읽기",
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
    
    if res.status_code == 200:
        print(f"✅ PC 최적화 v36.0 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
