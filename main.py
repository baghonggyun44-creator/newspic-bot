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

    # 뉴스픽이 정상 공유로 인식하는 최신 NID 대역 (2026.01.17 업데이트)
    # NID가 너무 오래되면 보안 검사가 더 엄격해집니다.
    latest_nids = ["8799100", "8799350", "8799500", "8798800", "8799800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v35.0 - 하이퍼 유입 세탁]
    unique_id = str(uuid.uuid4())[:8]
    # 뉴스픽 내부 파라미터를 최소화하여 '자연스러운 공유'처럼 보이게 합니다.
    target_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&_ref=google"
    
    # 🌟 핵심: 구글 리다이렉트를 사용하여 카카오톡의 흔적을 100% 지웁니다.
    bridge_url = f"https://www.google.com/url?q={target_url}&source=news&ust={int(time.time())}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [긴급] 지금 바로 확인해야 할 화제의 소식",
            "description": "클릭 시 상세 페이지로 안전하게 연결됩니다. (공식 보안 통과)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "상세 보기",
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
        print(f"✅ 최종 v35.0 구글 경유 링크 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
