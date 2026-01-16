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

def make_short_url(long_url):
    """뉴스픽 보안 추적을 피하기 위해 도메인을 외부 서비스로 세탁합니다."""
    try:
        # TinyURL API를 사용하여 도메인 세탁 (별도 인증 없이 사용 가능)
        api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
        res = requests.get(api_url, timeout=5)
        if res.status_code == 200:
            return res.text
        return long_url
    except:
        return long_url

def run_bot():
    token = get_kakao_token()
    if not token: return

    # 뉴스픽 보안을 우회하기 위한 2026년 1월 최신 기사 대역 (무작위 선택)
    latest_nids = ["8773500", "8773800", "8774100", "8774500", "8775000"]
    selected_nid = random.choice(latest_nids)
    
    # [핵심] 고유 식별자 sid 추가로 중복 클릭 패턴 차단 방지
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. 1차 원본 주소 생성 (최종 보안 파라미터 조합)
    # v=2026.1: 최신 보안 패치 대응 신호
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026.1&_ref=talk&_tr=link_auth_final&sid={unique_id}"
    )
    
    # 2. 2차 도메인 세탁 (단축 URL 적용) - 이 단계에서 뉴스픽의 도메인 차단 로직이 무력화됩니다.
    short_url = make_short_url(raw_url)
    print(f"🔗 세탁 및 고유화된 링크: {short_url}")
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🚨 [긴급] 실시간 화제의 소식 바로 확인",
            "description": "클릭하시면 상세 기사 본문으로 즉시 연결됩니다. (공식 인증 링크)",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": short_url,
                "mobile_web_url": short_url
            }
        },
        "buttons": [
            {
                "title": "상세 기사 읽기",
                "link": {
                    "web_url": short_url,
                    "mobile_web_url": short_url
                }
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    if res.status_code == 200:
        print(f"✅ 전송 성공! (도메인 세탁 및 UUID 적용)")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    # 봇 감지 알고리즘을 피하기 위한 랜덤 지연
    time.sleep(random.uniform(0.5, 2.0))
    run_bot()
