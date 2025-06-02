# ── Google API 호출을 좋아요한 재생목록 영상과 그 정보를 불러오는 모듈 ──

from tool import is_short, get_categoryId

# 좋아요 한 영상의 정보를 불러오는 함수
# youtube: 유튜브 객체
def extract_video_info_from_liked_playlist(youtube):
    # 호출한 좋아요 영상 정보를 담는 리스트
    like_video_info_list = []

    # 구글에 보낼 영상 정보 요청 사항
    # 재생목록 조회를 위한 API 요청 구성
    # videos(): 영상 관련 API 요청들을 포함한 리소스 생성
    # list(): API 요청 정보를 담고 있는 객체 생성
    # part: 파라미터 (어떤 정보만 받을지)
    # myRating: 
    # maxResults: 
    request = youtube.videos().list(
        part="snippet, contentDetails",
        myRating="like", #좋아요한 영상 재생목록
        maxResults=50 #최대 50개
    )

    # 
    while request:

        # 요청 받은 좋아요한 영상 정보
        response = request.execute()
        # item: 응답 받은 영상의 정보(dict)를 꺼냄 예) {"kind": "youtube#video", "id": "abc123", "snippet": {"title": "파이썬 강의","channelTitle": "코딩하는 정대리““category”: "Music"}}
        for info in response["items"]:

            # video_info_list에 추가할 영상 정보
            like_video_info = {
                "id": info["id"],
                "title": info["snippet"]["title"],
                "category": get_categoryId(info["snippet"].get("categoryId", "0")),
                "channel": info["snippet"]["channelTitle"],
                "thumbnails" : info['snippet']['thumbnails']['high'],
                "durationSec": info["contentDetails"]["duration"],
                "isShort": is_short(info),
                "video_url" : "https://www.youtube.com/watch?v=" + info["id"]
            }
            #like_video_info_list에 추가
            like_video_info_list.append(like_video_info)

        # 다음 영상 정보 요청 사항 생성
        # list_next: 자동으로 다음 페이지를 요청할 수 있는 request 객체를 반환하는 함수
        request = youtube.videos().list_next(request, response) 

    return like_video_info_list
'''
[
    {'id': 'fTwZNlF9K8E',
    'title': '閻羅 (cover)\u200b\u200b\u200b\u200b\u200b / \u200bヒュボク',
    'category': '10',
    'channel': '휴복',
    'thumbnails': {'url': 'https://i.ytimg.com/vi/fTwZNlF9K8E/hqdefault.jpg',
    'width': 480, 'height': 360}, 'durationSec': 273.0, 'isShort': 'notShort',
    'dateTimes': [datetime.datetime(2025, 5, 19, 0, 19, 31, 433000, tzinfo=tzutc())]
    },
    {
    .
    .
    .
    }
]
'''