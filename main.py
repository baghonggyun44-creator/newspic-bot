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
    # 저장된 토큰 파일을 사용하여 액세스 토큰을 자동으로 갱신합니다.
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

    # 뉴스픽 보안 엔진이 '정상 트래픽'으로 간주하는 2026년 1월 최신 기사 대역
    latest_nids = ["8777000", "8777200", "8777500", "8776800", "8777800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v12.0 - 구글 검색 엔진 경유 위장]
    # 뉴스픽 서버가 유입 경로를 추적할 때 카카오톡을 지우고 구글 검색으로 위장합니다.
    unique_id = str(uuid.uuid4())[:8]
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026_final&_ref=google&_tr=search_organic&sid={unique_id}"
    )
    
    # 🌟 핵심: 구글 리다이렉트 스키마를 사용하여 뉴스픽 보안 서버를 속입니다.
    bridge_url = f"https://www.google.com/url?q={raw_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔴 [실시간] 지금 바로 확인해야 할 화제의 뉴스",
            "description": "상세 기사 본문으로 안전하게 연결됩니다. (구글 보안 확인 완료)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "기사 전문 보기",
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
        print(f"✅ 구글 경유 위장 링크 전송 성공 (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
