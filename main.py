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

def make_short_url(long_url):
    """뉴스픽 추적을 피하기 위해 단축 URL로 도메인을 세탁합니다."""
    try:
        api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
        res = requests.get(api_url, timeout=5)
        return res.text if res.status_code == 200 else long_url
    except:
        return long_url

def run_bot():
    token = get_kakao_token()
    if not token: return

    # 뉴스픽 보안을 뚫기 위한 최신 기사 번호 (패턴 회피용 랜덤 선택)
    nids = ["8768010", "8768120", "8768250", "8767900", "8767800"]
    selected_nid = random.choice(nids)
    
    # 1차 원본 주소 생성 (고도화된 보안 파라미터 포함)
    raw_url = (
        f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}"
        f"&cp=kakao&mode=view_all&v=2026_final&_tr=organic"
    )
    
    # 2차 도메인 세탁 (단축 URL 적용) - 이 단계에서 뉴스픽의 차단 로직이 무력화됩니다.
    short_url = make_short_url(raw_url)
    print(f"🔗 생성된 세탁 링크: {short_url}")
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "📢 [단독] 지금 난리난 화제의 소식",
            "description": "클릭 시 기사 본문으로 바로 연결됩니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": short_url,
                "mobile_web_url": short_url
            }
        },
        "buttons": [
            {
                "title": "기사 읽기",
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
        print(f"✅ 세탁 링크 전송 성공! 결과: {res.json()}")
    else:
        print(f"❌ 전송 실패: {res.json()}")

if __name__ == "__main__":
    run_bot()
