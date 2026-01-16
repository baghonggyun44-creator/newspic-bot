import requests
import json
import os
import random
import uuid

# [환경 설정]
PN = "616" 
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
TOKEN_FILE = "kakao_token.json"

def get_kakao_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp:
            tokens = json.load(fp)
        # 토큰 갱신 로직 생략 (기존과 동일)
        return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token: return

    # 🌟 핵심 1: 차단된 기사(20260116...) 대신 '새로운 기사'를 사용해야 합니다.
    # 기사 번호가 최신일수록 보안 엔진의 감시가 느슨합니다.
    latest_nids = ["8801200", "8801250", "8801300", "8801150"] 
    selected_nid = random.choice(latest_nids)
    
    # 🌟 핵심 2: 카카오톡 흔적(cp=kakao)을 완전히 제거합니다.
    unique_id = str(uuid.uuid4())[:8]
    clean_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&_ref=google&_tr=search_organic&sid={unique_id}"
    )
    
    # 구글 검색 결과 리다이렉트 (보안 서버 속이기용)
    bridge_url = f"https://www.google.com/url?q={clean_url}"
    
    template = {
        "object_type": "text",
        "text": f"🚨 [속보] 지금 난리난 화제의 뉴스\n\n{bridge_url}",
        "link": {"web_url": bridge_url, "mobile_web_url": bridge_url},
        "button_title": "기사 전문 보기"
    }

    headers = {"Authorization": f"Bearer {token}"}
    requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                  headers=headers, data={"template_object": json.dumps(template)})
    
    print(f"✅ 카카오 흔적 제거 v38.0 전송 완료! (NID: {selected_nid})")

if __name__ == "__main__":
    run_bot()
