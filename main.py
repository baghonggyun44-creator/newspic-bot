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

    # 뉴스픽 보안 엔진이 '정상 트래픽'으로 간주하는 실시간 인기 기사 대역
    latest_nids = ["8790100", "8790350", "8790500", "8789800", "8790800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v26.0 - 구글 검색 위장]
    unique_id = str(uuid.uuid4())[:8]
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026_final&_ref=google&_tr=search_organic&sid={unique_id}"
    )
    
    # 🌟 핵심: 구글 리다이렉트 스키마를 사용하여 뉴스픽 보안 서버를 완벽하게 속입니다.
    # 대형 포털 유입은 뉴스픽 입장에서 차단 시 검색 노출 불이익이 있어 보안 검사가 매우 관대합니다.
    bridge_url = f"https://www.google.com/url?q={raw_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [속보] 지금 난리난 화제의 뉴스 바로 확인",
            "description": "상세 기사 본문으로 안전하게 연결됩니다. (공식 보안 확인 완료)",
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
