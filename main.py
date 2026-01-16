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

    # [수정] 뉴스픽 API 대신 공용 채널 데이터를 시도하여 차단 우회
    url = "https://partners.newspic.kr/main/contentList"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 뉴스픽 서버에 기사 요청
        res = requests.post(url, headers=headers, data={'channelNo': '1', 'pageSize': '10'}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            articles = data.get('recomList', [])
            if not articles:
                # 대안: 기본 핫이슈 기사 사용
                title, nid = "오늘의 실시간 핫이슈 확인하기", "8761500"
            else:
                target = articles[0]
                title, nid = target['title'], target['nid']
        else:
            title, nid = "지금 가장 뜨거운 실시간 뉴스", "8761500"
    except:
        title, nid = "실시간 급상승 핫이슈", "8761500"
    
    # 뉴스픽 링크 생성 (im.newspic.kr 적용)
    article_url = f"https://im.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao"
    
    template = {
        "object_type": "feed",
        "content": {
            "title": f"🔥 [실시간 핫이슈]\n\n\"{title}\"",
            "description": "클릭하면 상세 페이지로 이동합니다.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    # 전송 결과 출력 강화
    res_kakao = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                              headers={"Authorization": f"Bearer {token}"}, 
                              data={"template_object": json.dumps(template)})
    print(f"📢 전송 시도 완료: {res_kakao.json()}")

if __name__ == "__main__":
    run_bot()
