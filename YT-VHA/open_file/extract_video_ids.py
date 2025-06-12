# ── 리스트로 변환된 테이크 아웃 파일에 영상 URL에서 영상 id 추출하는 모듈 ──

import re

# takeout 파일에 모든 영상 아이디 추출하는 함수
def extract_video_ids(takeout):
    # 영상 id 목록 담을 리스트
    video_ids = []

    for item in takeout:
        # 영상 1개 id 추출
        match = is_id(item)
        if match:
            #영상 id를 저장
            video_ids.append(match)

    return video_ids


# 영상 1개 id 추출하는 함수
def is_id(item):
    # ex) "https://www.youtube.com/watch?v\u003d4ZAWSzma3DI&t=10s"
    url = item.get("titleUrl", "") #"titleUrl"이 없으면 빈 문자열을 대신 넣는다
    
    # 'v\u003d' 다음에 나오는 '&' 또는 문자열의 끝까지의 모든 문자를 캡처
    match = re.search(r"v=([^&]+)", url) 
    if match:
        return match.group(1)
    

'''
['fTwZNlF9K8E', 'hTwZgalF9Gdw' ...]
'''