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

    # 뉴스픽 보안 엔진이 '정상 트래픽'으로 간주하는 최신 기사 대역 (2026년 1월 기준)
    latest_nids = ["8772000", "8772200", "8772500", "8771800", "8772800"]
    selected_nid = random.choice(latest_nids)
    
    # [최종 보안 우회 v9.0 핵심]
    # 1. uuid4: 매 접속마다 고유 ID를 부여하여 중복 접속 차단 회피
    # 2. _tr=organic_share: 유료 광고가 아닌 자연스러운 공유 유입으로 위장
    # 3. mode=view_all: 리다이렉트 엔진을 강제로 종료시키고 상세 페이지 고정
    unique_id = str(uuid.uuid4())[:8]
    article_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026.1&_ref=talk&_tr=organic_share&sid={unique_id}"
    )
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "📺 [실시간 화제] 지금 난리난 핫이슈 확인하기",
            "description": "클릭하시면 뉴스픽 상세 기사로 즉시 연결됩니다. (공식 인증 링크)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 원문 보기",
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
        print(f"✅ 최종 우회 링크 전송 성공! (UUID: {unique_id})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    # 봇 감지 알고리즘을 피하기 위해 무작위 지연 실행
    time.sleep(random.uniform(0.1, 2.5))
    run_bot()
