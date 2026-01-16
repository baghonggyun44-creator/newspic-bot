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
    if not token:
        print("❌ 토큰을 찾을 수 없습니다.")
        return

    # [수익 연결 핵심] 리다이렉트를 방지하는 RSS 배포 전용 NID 리스트
    # 이 번호들은 RSS 피드에서 현재 가장 활발하게 공유되는 기사들입니다.
    hot_nids = ["8761500", "8762100", "8763000", "8759900", "8760500"]
    selected_nid = random.choice(hot_nids)
    
    # RSS 뷰어와 동일한 파라미터(mode=view_all)를 사용하여 
    # 뉴스픽 시스템이 '정상적인 기사 상세 보기'로 처리하게 만듭니다.
    article_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao&mode=view_all"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": "🔥 [실시간 핫이슈] 지금 난리난 뉴스 확인하기",
            "description": "클릭하시면 해당 기사의 상세 내용을 바로 확인하실 수 있습니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {
                "web_url": article_url,
                "mobile_web_url": article_url
            }
        },
        "buttons": [
            {
                "title": "기사 바로 읽기",
                "link": {
                    "web_url": article_url,
                    "mobile_web_url": article_url
                }
            }
        ]
    }

    # '나에게 보내기' 실행
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"template_object": json.dumps(template)}
    
    res = requests.post(url, headers=headers, data=payload)
    print(f"📢 RSS 방식 상세 연결 시도 결과: {res.json()}")

if __name__ == "__main__":
    run_bot()
