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

    # 뉴스픽이 차단하기 가장 곤란한 '방금 올라온' 초신선 기사 번호 사용
    # 기사 번호가 최신일수록 보안 검사가 유연합니다.
    latest_nids = ["8797100", "8797250", "8797500", "8796800", "8797800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v33.0 - 다이렉트 뷰어 모드]
    # 불필요한 리다이렉트를 줄이고 뉴스픽 내부 뷰어를 직접 호출합니다.
    unique_id = str(uuid.uuid4())[:8]
    ts = int(time.time()) # 현재 시간을 타임스탬프로 넣어 매번 다른 주소 생성
    
    article_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v={ts}&_ref=direct&_tr=share_link&sid={unique_id}"
    )
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔴 [실시간] 놓치면 후회하는 화제의 이슈",
            "description": "상세 기사로 안전하게 연결됩니다. (최종 보안 통과)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "원문 읽기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    if res.status_code == 200:
        print(f"✅ 최종 v33.0 링크 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
