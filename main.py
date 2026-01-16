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

    # [핵심] 리다이렉트를 방지하고 im.newspic.kr을 유지시키는 파라미터 조합
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # mode=view_all과 utm 인자를 조합하여 뉴스픽 보안 시스템이 '정상 클릭'으로 인식하게 합니다.
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=view_all&utm_campaign=share"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 지금 가장 뜨거운 뉴스",
            "description": "상세 내용을 보시려면 아래 버튼을 눌러주세요.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 상세보기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers={"Authorization": f"Bearer {token}"}, 
                        data={"template_object": json.dumps(template)})
    print(f"📢 리다이렉트 방어 전송 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
