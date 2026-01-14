import requests
import json
import os
import random

# [환경 설정]
PN = "638"
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
REDIRECT_URI = "http://localhost:5000"
TOKEN_FILE = "kakao_token.json"

# [핵심] 확인된 질문자님의 회원번호
TARGET_ID = "4689990492" 

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
        if 'refresh_token' in res: tokens['refresh_token'] = res['refresh_token']
        save_tokens(tokens)
        return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰 오류! KAKAO_CODE를 새로 업데이트하세요.")
        return

    # 기사 가져오기
    res = requests.post("https://partners.newspic.kr/main/contentList", data={'channelNo': '12', 'pageSize': '20'}).json()
    articles = res.get('recomList', [])
    if not articles: return
    
    target = articles[0]
    title = target['title']
    nid = target['nid']
    
    # [도메인 수정] im.newspic.kr 적용
    article_url = f"https://im.newspic.kr/view.html?nid={nid}&pn={PN}&cp=kakao&t={random.randint(1000, 9999)}"
    
    # 커버문구 적용
    final_text = f"🔥 [실시간 핫이슈]\n\n\"{title}\"\n\n지금 바로 확인해보세요!"

    template = {
        "object_type": "feed",
        "content": {
            "title": final_text,
            "description": "클릭 시 기사로 이동하여 상세 내용을 확인하세요.",
            "image_url": "https://m.newspic.kr/images/common/og_logo.png",
            "link": {"web_url": article_url, "mobile_web_url": article_url}
        },
        "buttons": [{"title": "기사 바로 읽기", "link": {"web_url": article_url, "mobile_web_url": article_url}}]
    }

    headers = {"Authorization": f"Bearer {token}"}
    
    # 친구 목록에서 UUID 추출 시도
    friends_res = requests.get("https://kapi.kakao.com/v1/api/talk/friends", headers=headers).json()
    target_uuid = None
    for f in friends_res.get('elements', []):
        if str(f.get('id')) == TARGET_ID:
            target_uuid = f['uuid']
            break

    if target_uuid:
        url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        payload = {"receiver_uuids": json.dumps([target_uuid]), "template_object": json.dumps(template)}
        r = requests.post(url, headers=headers, data=payload)
        print(f"✅ 전송 결과: {r.json()}")
    else:
        # 실패 시 나에게 보내기로 백업
        requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data={"template_object": json.dumps(template)})
        print("⚠️ 대상을 찾지 못해 '나에게 보내기'로 발송되었습니다.")

if __name__ == "__main__":
    run_bot()
