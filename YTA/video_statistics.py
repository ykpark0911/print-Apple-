# ── 시청기록 통계 자료를 만드는 모듈 ──

from collections import Counter, defaultdict
from tool import dateTime_iso8601_to_dateTime
from datetime import timezone, timedelta


# 좋아요 가장 많이 누른 채널 (상위 num개) 뽑아내는 함수
# like_list: 좋아요 재생목록의 영상 정보담긴 파일(리스트)
# num: 뽑아낼 채널 개수(int)
def get_top_like_channel(like_list, num):
    channel_list= []
    for item in like_list:
        channel = item["channel"]
        channel_list.append(channel)

    
    channel_count = Counter(channel_list)
    top_channels = channel_count.most_common(num)

    return top_channels # channel_count({'침착맨': 50, '빠더너스': 32, .....})


# 가장 많이 본 채널 (상위 num개) 뽑아내는 함수
# takeout: takeout 파일(리스트)
# num: 뽑아낼 채널 개수(int)
def get_top_channel(takeout, num): 
    channel_list= []
    for item in takeout:
        channel = item["subtitles"][0]["name"]
        channel_list.append(channel)

    
    channel_count = Counter(channel_list)
    top_channels = channel_count.most_common(num)
    
    return top_channels # channel_count({'침착맨': 50, '빠더너스': 32, .....})


# 시간별 영상 시청 개수 새는 함수
def get_hour_distribution(takeout):
    KST = timezone(timedelta(hours=9))
    hour_list = []
    
    for item in takeout:
        dt = dateTime_iso8601_to_dateTime(item["time"])
        local_dt = dt.astimezone(KST) #지역 시간대로 변경
        hour_list.append(local_dt.hour)  # datetime 객체에서 시간만 추출

    hour_count = Counter(hour_list)
    hours = list(range(24))
    counts = [hour_count.get(hour, 0) for hour in hours]

    return hours, counts


# 날짜별 영상 시청 개수 새는 함수
# group_by: "day"(하루), "week"(주), "month"(달), "weekDay"(요일)로 분류 가능
def get_date_distribution(takeout, group_by):
    group_date_list = [] #선택한 데이터 종류 저장 받는 곳
    dates_list = defaultdict(set)  # 시청한 날짜를 datetime 형태로 저장받는 곳
    
    for item in takeout:
        dt = dateTime_iso8601_to_dateTime(item["time"]).date()
        
        if group_by == "day":
            key = dt.strftime("%Y-%m-%d")

        elif group_by == "week":
            # 주 시작(월요일)
            week_start = dt - timedelta(days=dt.weekday()) #dt.weekday()는 요일을 숫자로 변환... 월요일 = 0
            # 주 끝(일요일)
            week_end = week_start + timedelta(days=6)
            # 포맷: YYYY년 MM월 DD일 ~ MM월 DD일
            key = f"{week_start.year}-{week_start.month:02d}-{week_start.day:02d} ~ {week_end.month:02d}-{week_end.day:02d}"
            dates_list[key].add(dt)

        elif group_by == "month":
            key = dt.strftime("%Y-%m")
            dates_list[key].add(dt)

        elif group_by == "weekDay":
            key = dt.strftime("%A")
        
        group_date_list.append(key)
    
    group_date_list = Counter(group_date_list)
    
    sorted_items = sorted(group_date_list.items())
    
    #키와 값을 분리
    group_dates, group_counts = [], []
    for i in sorted_items:
        group_dates.append(i[0])
        group_counts.append(i[1])
    

    if group_by == "week" or group_by == "month":
        average_group_counts = []
        for j in group_dates:
            dates_count = len(dates_list[j]) #분석 종류에 해당하는 날짜 갯수
            avg = group_date_list[j]//dates_count #분석 종류의 카운트를 일별 평균으로 구함
            average_group_counts.append(avg)
        return group_dates, (group_counts, average_group_counts)
    else :
        return group_dates, group_counts


# 카테고리별 영상 시청 개수 새는 함수
# video_info_list: 응답 받은 정보 있는 파일(리스트)
def get_category_distribution(video_info_list):
    category_list =[]

    for item in video_info_list:
        category = item["category"]
        category_list.append(category)
    category_count = Counter(category_list)

    sorted_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)  # 많이 본 순

    #각각 카테고리 이름과 해당 카테고리의 영상 수를 따로 분리해 리스트로
    categories, counts = [], []
    for i in sorted_categories:
        categories.append(i[0])
        counts.append(i[1])

    return categories, counts