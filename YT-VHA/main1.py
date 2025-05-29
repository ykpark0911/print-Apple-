# 시청기록으로 정보 뽑아내기
from open_file.extract_video_ids import extract_video_ids_from_watch_history # 영상 id 뽑아내는 함수
from open_file.json_loader import load_json # takeout 파일 여는 함수
from yt_api.get_video_info import get_video_info, for_time_get_short_count, get_error_count #영상 정보 호출하는 함수
from yt_api.oauth import get_authenticated_service # 유튜브 객체 만드는 함수
from filter import not_short_filter # 쇼츠 영상 제외 시키는 필터 함수 


def file_load():
    # 유튜브 객체 생성
    youtube = get_authenticated_service()
    print("인증 완료")

    # takeout 파일 경로
    path = "C:\\pypy\\print-Apple-\\YT-VHA\\open_file\\Takeout\\YouTube 및 YouTube Music\\시청 기록\\시청 기록2006.json"

    # json 파일 리스트로 변환
    video_list= load_json(path)
    print("테이크 아웃 파일 불러오기 완료")

    # 쇼츠 영상 제외
    not_short_video_list= not_short_filter(video_list)


    total_watch_video = len(video_list) # takeout 파일 총 영상 개수
    total_not_short_video = len(not_short_video_list) # takeout 파일 쇼츠 제외한 영상 개수
    total_short_video = total_watch_video - total_not_short_video # takeout 파일 쇼츠 영상 개수

    # 영상 id 추출
    video_ids= extract_video_ids_from_watch_history(not_short_video_list)
    print("아이디 추출 완료")

    # 영상 정보 호출
    video_info_list= get_video_info(youtube, video_ids, not_short_video_list)
    print("영상 정보 호출 완료")


    total_not_short_video2 = len(not_short_video_list) # 쇼츠 제외 영상 개수
    total_short_video2 = total_short_video + for_time_get_short_count() # 쇼츠 영상 개수
    error_video = get_error_count() # 에러 영상 개수

    print(video_info_list)

    print(f"불러온 영상: {total_watch_video}, 시간 차로 뽑아낸 쇼츠 영상: {total_short_video}")
    print(f"추정 쇼츠 제외 영상: {total_not_short_video2}, 총 추청 쇼츠 영상: {total_short_video2}")
    print(f"오류 영상: {error_video}")


'''
영상 정보 호출 완료
불러온 영상: 30736, 시간 차로 뽑아낸 쇼츠: 28364
정재된 영상: 1925, 총 추청 쇼츠: 28810
오류 영상: 1
'''