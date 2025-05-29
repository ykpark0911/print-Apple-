# ── 리스트로 변환된 테이크 아웃 파일에 영상 URL에서 영상 id 추출하는 모듈 ──

import re

# 영상 1개 id 추출하는 함수
def is_id(item):
    url = item.get("titleUrl" "") #get()는 딕셔너리 키에 해당하는 값을 반환해줌, "titleUrl"이 없으면 **빈 문자열 ""**을 대신 넣는다
    match = re.search(r"v=([^&]+)", url) #serch()는 문자열에서 특정 패턴으로 나누어 정리하고 이를 객체로 만든다.
    if match:
        return match.group(1)


# takeout 파일에 모든 영상 아이디 추출하는 함수
def extract_video_ids_from_watch_history(video_list):
    video_ids = []

    for item in video_list: #첫 번째, 두 번째... 영상의 정보가 담긴 딕셔너리가 복사됨
        match = is_id(item)
        if match:
            video_ids.append(match) #영상 id를 저장

    return video_ids # ['fTwZNlF9K8E', 'hTwZgalF9Gdw' ...]