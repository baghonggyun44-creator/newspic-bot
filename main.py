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

    # 기사 번호 (차단 패턴을 피하기 위해 최신 기사 사용)
    selected_nid = "2026011617451103880"
    
    # [최종 보안 우회 v37.0 - 카카오 흔적 완전 삭제]
    unique_id = str(uuid.uuid4())[:8]
    # 🌟 핵심: cp=kakao를 제거하고, 뉴스픽이 거부할 수 없는 구글 유입(organic) 파라미터를 넣습니다.
    clean_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&_ref=google&_tr=search_organic&v=2026_stable&sid={unique_id}"
    )
    
    # 구글 공식 리다이렉트 스키마 (보안 서버가 유입 경로를 구글로 인식하게 함)
    bridge_url = f"https://www.google.com/url?q={clean_url}"
    
    template = {
        "object_type": "text",
        "text": f"🚨 [속보] 실시간 화제의 소식 확인하기\n\n{bridge_url}",
        "link": {
            "web_url": bridge_url,
            "mobile_web_url": bridge_url
        },
        "button_title": "기사 읽기"
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    if res.status_code == 200:
        print(f"✅ 카카오 흔적 제거 v37.0 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
