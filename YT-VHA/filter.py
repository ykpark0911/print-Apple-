from tool import dateTime_iso8601_to_dateTime

# 쇼츠 영상 제외 하는 필터 함수
# takeout: takeout 파일(리스트)
def not_short_filter(takeout):
    not_short_takeout= []
    
    for i in range(len(takeout) - 1):
        # 비교할 데이터 2개
        # takeout 파일은 최신순으로 정렬되어있음
        # now_data = 현재 쇼츠인지 판별할 영상의 데이터
        # next_data = now_data 바로 이전에 보았던 영상
        now_data = dateTime_iso8601_to_dateTime(takeout[i]["time"])
        befo_data = dateTime_iso8601_to_dateTime(takeout[i+1]["time"])

        # 현재 영상 - 이전 영상의  영상의 시간차
        time_diffrence_sec1 = (now_data- befo_data).total_seconds()

        if i == 1:
            if time_diffrence_sec1 > 60:
                not_short_takeout.append(takeout[i])
        else:         
            # before_data = now_data 바로 다음에 보았던 영상 (i == 1일 때는 영상의 경우에는 없으니까 스킵함)
            next_data = dateTime_iso8601_to_dateTime(takeout[i-1]["time"])
            # 다음 영상 - 현재 영상의  영상의 시간차
            time_diffrence_sec2 = (next_data- now_data).total_seconds()
            if time_diffrence_sec2 > 60 and time_diffrence_sec1 > 60:
                not_short_takeout.append(takeout[i])
    
    return not_short_takeout


# 유튜브 뮤직에서 본 영상과 유튜브에서 본 영상 분류하는 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
def music_and_not_music_filter(video_info_list):
    music_video_info_list = []
    not_music_video_info_list = []
    for item in range(video_info_list):
        if item["platform"] == "YouTube Music":
            music_video_info_list.append(item)
        else :
            not_music_video_info_list.append(item)
    
    return music_video_info_list, not_music_video_info_list


# 선택한 카테고리에 해당하는 영상을 뽑아내는 필터 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
# select_category: 필터링할 카테고리 이름(str)
def category_filter(vedio_info_list, select_category):
    filtered_viedio_info_list = []
    for item in vedio_info_list:
        if item.get("categoryId") == select_category:
            filtered_viedio_info_list.append(item)

        return filtered_viedio_info_list


# 선택한 채널에 해당하는 영상을 뽑아내는 필터 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
# select_channel: 필터링할 채널 이름(str)
def channel_filter(vedio_info_list, select_channel):
    filtered_viedio_info_list = []
    for item in vedio_info_list:
        if item.get("channel") == select_channel:
            filtered_viedio_info_list.append(item)

        return filtered_viedio_info_list
    

# 선택한 날짜에 해당하는 영상을 뽑아내는 필터 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
# select_channel: 필터링할 날짜 (datetime.date 객체)
def date_filter(video_info_list, target_date):
    filtered_video_info_list = []
    for item in video_info_list:
        dt = item.get("dateTime")
        if dt.date() == target_date:
            filtered_video_info_list.append(item)

    return filtered_video_info_list


# 구독한 채널에 영상을 뽑아내는 필터 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
def sub_filter(video_info_list):
    filtered_video_info_list = []
    for item in video_info_list:
        if item["sub"] == "sub":
            filtered_video_info_list.append(item)

    return filtered_video_info_list