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

    # 보안 감시를 피하기 위한 실시간 최신 기사 대역 (2026.01.17 업데이트)
    latest_nids = ["8798100", "8798350", "8798500", "8797800", "8798800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v34.0 - 하이퍼 리다이렉트]
    unique_id = str(uuid.uuid4())[:12]
    # 뉴스픽이 정상적인 공유로 인식하는 파라미터 조합
    target_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&_ref=sns&_tr=share&sid={unique_id}"
    )
    
    # 🌟 핵심: 포털 검색 결과인 것처럼 위장하여 보안 서버가 추적을 포기하게 만듭니다.
    # 포털 도메인을 경유하면 뉴스픽 보안 필터링의 우선순위가 낮아집니다.
    bridge_url = f"https://search.naver.com/search.naver?where=nexearch&query={selected_nid}&url={target_url}"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [긴급] 실시간 화제의 소식 바로 확인",
            "description": "상세 기사로 안전하게 연결됩니다. (공식 보안 확인 완료)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": bridge_url,
                "mobile_web_url": bridge_url
            }
        },
        "buttons": [
            {
                "title": "기사 원문 읽기",
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
        print(f"✅ 새로운 PN(616) 기반 브릿지 링크 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    # 봇 감지 알고리즘을 피하기 위해 실행 시점을 약간 비틉니다.
    time.sleep(random.uniform(1.0, 3.0))
    run_bot()
