#시청기록으로 좋아요한 영상 정보 뽑아내기

from yt_api.get_yt_ob import tester_login
from yt_api.get_like_video_info import extract_video_info_from_like_playlist


def like_load():
    # 유튜브 객체 생성
    youtube = tester_login()
    print("인증 완료")

    # 좋아요 한 영상 정보 호출
    like_list= extract_video_info_from_like_playlist(youtube)
    
    print(like_list)


like_load()