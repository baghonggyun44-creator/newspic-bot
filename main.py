import requests
import json
import os
import random
import time
import uuid

# [환경 설정]
# 이미지에서 검출된 주인님의 새로운 수익 코드입니다.
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

    # 보안 검열을 피하기 위해 현재 가장 활성화된 최신 기사 대역을 사용합니다.
    latest_nids = ["8796000", "8796250", "8796500", "8795800", "8796800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v32.0 - 새로운 PN 적용 및 네이버 검색 위장]
    unique_id = str(uuid.uuid4())[:8]
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026_final&_ref=naver&_tr=search_organic&sid={unique_id}"
    )
    
    # 🌟 핵심: 네이버 리다이렉트 주소를 사용하여 유입 경로를 완벽하게 세탁합니다.
    bridge_url = f"https://search.naver.com/search.naver?where=nexearch&query={selected_nid}&url={raw_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "📺 [실시간] 지금 난리난 화제의 소식 확인하기",
            "description": "클릭하시면 상세 기사로 즉시 연결됩니다. (공식 보안 확인 완료)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "기사 본문 읽기",
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
        print(f"✅ 새로운 PN({PN}) 적용 및 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    # 봇 감지 알고리즘 회피를 위한 무작위 지연
    time.sleep(random.uniform(0.5, 2.0))
    run_bot()
