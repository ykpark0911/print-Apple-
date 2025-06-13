#  ── 기타 분석용 모듈 ──

import isodate
from dateutil import parser #pip install python-dateutil


# 카테고리 번호를 통해 카테고리 얻는 함수
# categoryId: 카테고리 id(str)
def get_categoryId(categoryId):
    category_id_map = {
    "0": "Unknown",
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "20": "Gaming",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "29": "Nonprofits & Activism"
}
    category= category_id_map.get(categoryId, "Unknown")

    return category


# iso8601 날짜를 datetime 형식의 날짜로 변환하는 함수
# dateTime_iso8601: iso8601 형식의 날짜(str)
def dateTime_iso8601_to_dateTime(dateTime_iso8601):
    duration = parser.isoparse(dateTime_iso8601)
    return duration


# iso8601 시간을 datetime 형식의 시간(초)로 변환하는 함수
# duration_iso8601: iso8601 형식의 시간(str)
def duration_iso8601_to_seconds(duration_iso8601):
    sec = isodate.parse_duration(duration_iso8601).total_seconds()
    return sec


# 쇼츠 영상인지 판별하는 함수
# item: 응답 받은 영상의 정보(dict)
def is_short(item):
    # duration 추출
    duration_iso8601 = item['contentDetails'].get("duration", "최초 공개 영상")
    if duration_iso8601 == "최초 공개 영상":
        return "최초 공개 영상"
    
    sec = duration_iso8601_to_seconds(duration_iso8601)

    # 60초 이하면 쇼츠로 판단
    if sec <= 60:
        return "shorts"
    else:
        return "not shorts"


# 구독한 채널의 영상인지 판별하는 함수
# item: 응답 받은 영상의 정보(dict)
def is_sub(item, sub_list):
    # 구독자 목록 불러오기
    if item["snippet"]["channelTitle"] in sub_list:
        return "sub"
    else:
        return "notSub"