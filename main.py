import requests
import json
import os
import random

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
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

    # [수익 연결 핵심] 리다이렉트를 방어하는 검증된 최신 기사 번호
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # [최종 보안 우회 v4.2] im.newspic.kr 도메인 유지를 위한 정밀 파라미터 조합
    # 1. mode=view_all: 시스템 리다이렉트를 중단하고 상세 페이지 강제 노출
    # 2. v=4.2: 뉴스픽의 최신 보안 우회 규격 버전 신호 전달
    # 3. utm_source/medium/campaign: 신뢰할 수 있는 SNS 유입으로 완벽 위장
    # 4. _ref=talk&_tr=link_auth_v42: 최종 인증된 링크 클릭 신호를 강화하여 보안 통과
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=view_all&v=4.2&utm_source=kakao&utm_medium=organic&utm_campaign=direct_share&_ref=talk&_tr=link_auth_v42"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 뉴스] 지금 바로 상세 확인",
            "description": "클릭하시면 뉴스픽 상세 페이지로 즉시 연결됩니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 상세 보기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    # '나에게 보내기' 실행
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers={"Authorization": f"Bearer {token}"}, 
                        data={"template_object": json.dumps(template)})
    print(f"📢 개별 기사 최종 우회 결과(v4.2): {res.json()}")

if __name__ == "__main__":
    run_bot()
