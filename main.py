import requests
import json
import os
import random
import time

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

def save_tokens(tokens):
    with open(TOKEN_FILE, "w") as fp:
        json.dump(tokens, fp)

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp:
            return json.load(fp)
    return None

def get_kakao_token():
    tokens = load_tokens()
    if not tokens:
        code = os.environ.get('KAKAO_CODE')
        if not code: return None
        url = "https://kauth.kakao.com/oauth/token"
        data = {"grant_type": "authorization_code", "client_id": REST_API_KEY, "redirect_uri": REDIRECT_URI, "code": code.strip()}
        res = requests.post(url, data=data).json()
        if 'access_token' in res:
            save_tokens(res)
            return res['access_token']
        return None
    
    url = "https://kauth.kakao.com/oauth/token"
    data = {"grant_type": "refresh_token", "client_id": REST_API_KEY, "refresh_token": tokens['refresh_token']}
    res = requests.post(url, data=data).json()
    if 'access_token' in res:
        tokens['access_token'] = res['access_token']
        save_tokens(tokens)
        return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰 오류! KAKAO_CODE를 새로 업데이트하세요.")
        return

    # [수정] 뉴스픽 서버 보안 우회를 위한 정밀 헤더 설정
    url = "https://partners.newspic.kr/main/contentList"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://partners.newspic.kr/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 뉴스픽 서버에 기사 목록 요청 (최대 3회 시도)
        target = None
        for _ in range(3):
            res = requests.post(url, headers=headers, data={'channelNo': '12', 'pageSize': '20'}, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get('recomList'):
                    target = data['recomList'][0]
                    break
            time.sleep(1)
        
        if not target:
            print("⚠️ 뉴스픽에서 기사를 가져오지 못했습니다. (서버 응답 없음)")
            return
    except Exception as e:
        print(f"❌ 뉴스픽 데이터 처리 중 오류: {e}")
        return
    
    # 뉴스픽 링크 생성 (사용자님의 im.newspic.kr 적용)
    article_url = f"https://im.newspic.kr/view.html?nid={target['nid']}&pn={PN}&cp=kakao"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": f"🔥 [실시간 핫이슈]\n\n\"{target['title']}\"",
            "description": "클릭하면 상세 페이지로 이동합니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    # 카카오톡 전송
    res_kakao = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                              headers={"Authorization": f"Bearer {token}"}, 
                              data={"template_object": json.dumps(template)})
    print(f"📢 전송 결과: {res_kakao.json()}")

if __name__ == "__main__":
    run_bot()
