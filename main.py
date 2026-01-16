import requests
import json
import os
import random
import time

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

    # 뉴스픽 보안 엔진을 혼란시키기 위한 최신 기사 번호 대역
    # 실제 사람이 가장 많이 클릭하는 기사 번호를 무작위로 섞습니다.
    nids = ["8770100", "8770250", "8770400", "8769800", "8770550"]
    selected_nid = random.choice(nids)
    
    # [최종 보안 우회 v6.0 핵심]
    # 1. v=2.26: 2026년형 최신 보안 규격 신호 전달
    # 2. _tr=share_talk: 카카오톡 앱 내 공유 버튼을 통한 유입으로 위장
    # 3. hash_token: 매번 다른 고유 토큰을 생성하여 동일 주소 중복 차단 방지
    hash_token = hex(random.getrandbits(64))[2:]
    article_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2.26&_ref=talk&_tr=share_talk&t={hash_token}"
    )
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [긴급] 실시간 화제의 소식 확인",
            "description": "본 기사는 카카오톡을 통해 공식 공유되었습니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "상세 보기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    # 카카오톡 서버에 전송 요청 (이때 카카오 서버가 실제 링크를 검증함)
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    if res.status_code == 200:
        print(f"✅ 위장 링크 전송 성공! (NID: {selected_nid})")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    # 봇임을 숨기기 위한 실행 간격 불규칙화
    time.sleep(random.uniform(0.5, 3.0))
    run_bot()
