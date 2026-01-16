import requests
import json
import os
import random
import time

# [환경 설정]
PN = "616" 
REST_API_KEY = "f7d16dba2e9a7e819d1e22146b94732e"
TOKEN_FILE = "kakao_token.json"

def get_kakao_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as fp:
            tokens = json.load(fp)
        
        # 토큰 유효성 즉시 확인
        test_url = "https://kapi.kakao.com/v1/user/access_token_info"
        test_res = requests.get(test_url, headers={"Authorization": f"Bearer {tokens['access_token']}"})
        
        if test_res.status_code != 200: # 토큰이 만료되었다면 갱신
            url = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": REST_API_KEY,
                "refresh_token": tokens['refresh_token']
            }
            res = requests.post(url, data=data).json()
            if 'access_token' in res:
                tokens['access_token'] = res['access_token']
                # 리프레시 토큰도 새로 오면 업데이트
                if 'refresh_token' in res:
                    tokens['refresh_token'] = res['refresh_token']
                with open(TOKEN_FILE, "w") as fp: json.dump(tokens, fp)
                return tokens['access_token']
        else:
            return tokens['access_token']
    return None

def run_bot():
    token = get_kakao_token()
    if not token:
        print("❌ 토큰을 가져올 수 없습니다. 인증을 다시 진행해주세요.")
        return

    # 최신 뉴스 번호 (2026.01.17 업데이트)
    selected_nid = "2026011617451103880" # 이미지에 나온 최신 NID 사용
    
    # [최종 우회 구조]
    # 필터링을 피하기 위해 텍스트 메시지 내부에 구글 경유 링크를 넣습니다.
    target_url = f"https://im.newspic.kr/view.html?nid={selected_nid}&pn={PN}&cp=kakao"
    bridge_url = f"https://www.google.com/url?q={target_url}"
    
    # 피드 타입 대신 텍스트 타입으로 전송 (스팸 필터 회피율 높음)
    template = {
        "object_type": "text",
        "text": f"🚨 [속보] 화제의 뉴스 확인하기\n\n{bridge_url}",
        "link": {
            "web_url": bridge_url,
            "mobile_web_url": bridge_url
        },
        "button_title": "기사 읽기"
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", 
                        headers=headers, 
                        data={"template_object": json.dumps(template)})
    
    if res.status_code == 200:
        print(f"✅ 전송 명령 성공! 나에게 보내기 확인 요망 (NID: {selected_nid})")
    else:
        # 에러 상세 내용을 출력하여 원인을 파악합니다.
        print(f"❌ 전송 실패 원인: {res.json()}")

if __name__ == "__main__":
    run_bot()
