# ── Google API 호출을 영상 id로 영상 정보 불러오는 모듈 ──

from tool import duration_iso8601_to_seconds, get_categoryId, is_short, is_sub

# 영상 id를 통해 영상 정보를 호출하고, 추가로 takeout 파일에 정보를 붙이는 함수
# 오류가 있거나 쇼츠 영상 발견시, 해당 영상을 제거(takeout 파일과 video_ids 리스트에서 실제로 삭제)
# youtube: 유튜브 객체
# video_ids: 호출할 영상 id 목록(list)
# takeout: takeout 파일(리스트)
def get_video_info(youtube, video_ids, takeout, sub_list):
    # 추가로 영상 시간을 통해 걸러진 쇼츠 영상 개수, 오류 영상 개수

    # 호출한 영상 정보를 담는 리스트
    video_info_list = []

    # 삭제할 영상의 인덱스 번호를 담는 리스트
    del_list = []

    # 불러온 영상 id의 개수
    video_num = len(video_ids)
    print(f"{video_num}개의 영상 불러옴")


    # 영상 id들을 50개 단위로 나눠서 요청 (API 제한)
    # i: 호출할 첫 번째 영상의 인덱스(int)를 꺼냄
    # video_ids, takeo t는 개수가 같고, i를 통해 에 접근 가능
    for i in range(0, video_num, 50):
        # 호출할 영상의 개수
        chunk = 50
        # 마지막으로 호출할 영상의 개수
        if i + 50> video_num:
            chunk = video_num - i

        print(f"요청 중: {i} ~ {i+chunk}")

        # video_ids와 takeout 파일을 chunk_num개 저장
        chunk_id = video_ids[i:i + chunk]
        chunk_list = takeout[i:i + chunk]


        # 구글에 보낼 영상 정보 요청 사항
        # videos(): 영상 관련 API 요청들을 포함한 리소스 생성
        # list(): API 요청 정보를 담고 있는 객체 생성
        # part: 파라미터 (어떤 정보만 받을지)
        # id: 요청할 영상 id들
        request = youtube.videos().list(
            part="snippet,contentDetails", 
            id=",".join(chunk_id) # 요청할 id를 한줄로 이어 붙임
        )

        # 요청 받은 영상 정보
        response = request.execute()
        '''
        response =
        {
            "items": [
                {
                "kind": "youtube#video",
                .
                .
                .
                },

                {
                .
                .
                .
                }

            ]
        '''

        # 응답 받은 영상 정보를 딕셔너리{id1 : item1, id2 : item2,...}형태로 저장
        response_dict = {}
        # item: 응답 받은 영상의 정보(dict)를 꺼냄 예)
        '''
        {
            "kind": "youtube#video",
            "id": "abc123",
            "snippet": {
                "title": "파이썬 강의",
                "channelTitle": "코딩하는 정대리",
                "categoryId": "10",
                "publishedAt": "2023-03-20T12:00:00Z",
                "thumbnails": {
                    "default": {
                    "url": "https://i.ytimg.com/vi/abc123/default.jpg",
                    "width": 120,
                    "height": 90
                    },
                    "high": {
                    "url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
                    "width": 480,
                    "height": 360
                    }
                }
            },
            "contentDetails": {
                "duration": "PT5M12S",
                "dimension": "2d",
                "definition": "hd"
            }
        }
        '''
        
        for item in response["items"]:
            response_dict[item["id"]] = item

        # 응답 받은 영상들을 저장하기 위해 순회
        # j: cunk에서 영상의 인덱스(int)를 꺼냄
        # i + j: 영상의 인덱스
        # id: 청크 영상 id(str)를 꺼냄 예) "Ffwfdfa123"
        for j, id in enumerate(chunk_id):
            
            # 청크 영상 id가 응답 받은 영상 id 목록에 없다면 오류 영상으로 판단
            if id not in response_dict:
                print(f"{i + j}번째 영상은 응답 없음 → 제거 대상")
                del_list.append(i + j)
                continue
            
            # 응답 받은 영상의 정보 (= item)
            info = response_dict[id]

            # 영상이 "shorts" 쇼츠 영상으로 판단
            if is_short(info) == "short":
                duration_sec = duration_iso8601_to_seconds(info["contentDetails"]["duration"])
                print(f"{i + j}번째인 {info["snippet"]["title"]} 영상은 {duration_sec}초로 쇼츠로 판별됨 → 제거 대상")
                del_list.append(i + j)
                continue
            
            # video_info_list에 추가할 영상 정보
            video_info = {
                "id": info["id"],
                "title": info["snippet"]["title"],
                "category": get_categoryId(info["snippet"].get("categoryId", "0")),
                "sub" : is_sub(info, sub_list),
                "channel": info["snippet"]["channelTitle"],
                "thumbnails": info['snippet']['thumbnails']['high'],
                "durationSec": info["contentDetails"]["duration"],
                "dateTime":  chunk_list[j]["time"],
                "platform" : chunk_list[j]["header"],
                "video_url" : "https://www.youtube.com/watch?v=" + info["id"]
            }
            # video_info_list에 추가
            video_info_list.append(video_info)

            print(f"{i + j}번째 영상 정보 뽑기 완료")

    #제거할 목록 제거
    # 뒤에서부터 제거 
    del_list.reverse()
    # 제거할 목록을 제거하기 위해서 순회
    # d: 제거할 목록의 인덱스 번호(int)
    for d in del_list:
        del video_ids[d]
        del takeout[d]

    return video_info_list
'''
{'id': 'bc3DJ2Up8j8',
'title': '일본 교토에서 부부즈케를 주는 이유',
'category': '22',
'channel': '와사비',
'thumbnails': {'url': 'https://i.ytimg.com/vi/bc3DJ2Up8j8/hqdefault.jpg', 'width': 480, 'height': 360},
'durationSec': 17.0,
'isShort': 'short',
'dateTime': datetime.datetime(2025, 5, 13, 10, 10, 0, 142000, tzinfo=datetime.timezone.utc)}]
'''