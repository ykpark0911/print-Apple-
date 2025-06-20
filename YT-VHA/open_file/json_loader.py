#  ── takeout.json 파일 여는 모듈 ──

import json
from open_file.extract_video_ids import is_id


# takeout 파일 여는 함수
def load_takeout_file(load_takeout_file_path):
    with open(load_takeout_file_path, "r", encoding="utf-8") as f:
        data = json.load(f) #load()는 파이썬의 리스트나 딕셔너리 자료형으로 바꿔준다.
    
    # 오류 영상을 제외한 일반적인 영상을 담을 리스트
    filtered_data = []

    # 오류 영상: "최초공개 영상", "유튜브 광고", "비공개 영상", "삭제 영상"
    for item in data:
        if (
        "titleUrl" in item and
        "subtitles" in item and
        "time" in item and
        "title" in item and
        is_id(item) and
        not item["title"].startswith("비공개") and
        not item["title"].startswith("삭제") and
        "/watch?v=" in item["titleUrl"]
        ):
            filtered_data.append(item)

    return filtered_data


def load_save_file(save_file_path):
    with open(save_file_path, "r", encoding="utf-8") as f: #with 문 안에 있는 코드 실행 후, 자동으로 파일 닫아준다.
        data = json.load(f) #load()는 파이썬의 리스트나 딕셔너리 자료형으로 바꿔준다.

    return data

'''
[
  {
  "header": "YouTube",
  "title": "감동 디스트로이어 을(를) 시청했습니다.",
  "titleUrl": "https://www.youtube.com/watch?v\u003d4ZAWSzma3DI",
  "subtitles": [{
    "name": "침착맨",
    "url": "https://www.youtube.com/channel/UCUj6rrhMTR9pipbAWBAMvUQ"
  }],
  "time": "2025-05-19T04:07:19.714Z",
  "products": ["YouTube"],
  "activityControls": ["YouTube 시청 기록"]
  },

  {
  .
  .
  .
  }
]
'''
