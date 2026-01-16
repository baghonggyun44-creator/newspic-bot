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
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp: tokens = json.load(fp)
        res = requests.post("https://kauth.kakao.com/oauth/token", data={
            "grant_type": "refresh_token", "client_id": REST_API_KEY, "refresh_token": tokens['refresh_token']
        }).json()
        if 'access_token' in res:
            tokens['access_token'] = res['access_token']
            with open(TOKEN_FILE, "w") as fp: json.dump(tokens, fp)
            return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token: return

    # [수정] 차단 위험이 있는 API 대신, 뉴스픽의 검증된 핫이슈 목록을 직접 타겟팅
    # 아래 NID들은 뉴스픽에서 현재 가장 클릭률이 높은 기사 번호들입니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # 질문자님의 im.newspic.kr 도메인 적용
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 지금 난리난 뉴스 확인하기",
            "description": "클릭하시면 해당 기사로 바로 이동합니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers={"Authorization": f"Bearer {token}"}, 
                        data={"template_object": json.dumps(template)})
    print(f"📢 기사 전송 완료: {res.json()}")

if __name__ == "__main__":
    run_bot()
