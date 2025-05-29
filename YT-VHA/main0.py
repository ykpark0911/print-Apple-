# 그래프 그리기
import matplotlib.pyplot as plt # 그래프 그릴 수 있게 해주는 라이브러리 #pip install matplotlib
from open_file.json_loader import load_json # takeout 파일 여는 함수
from video_statistics import get_top_channel, get_hour_distribution, get_date_distribution # 영상 통계내는 함수
from grape import plot_hour_distribution, plot_date_distribution, draw_pie_chart # 그래프 만드는 함수
from filter import not_short_filter # 쇼츠 영상 제외 시키는 필터 함수 


def grape_load():
    # takeout 파일 경로
    path = "C:\\pypy\\print-Apple-\\YT-VHA\\open_file\\Takeout\\YouTube 및 YouTube Music\\시청 기록\\시청 기록2006.json"

    # json 파일 리스트로 변환
    video_list= load_json(path)
    print("테이크 아웃 파일 불러오기 완료")
    
    # 쇼츠 영상 제외
    not_short_video_list = not_short_filter(video_list)

    total_watch_video = len(video_list) # takeout 파일 총 영상 개수
    total_not_short_video = len(not_short_video_list) # takeout 파일 쇼츠 제외한 영상 개수
    total_short_video = total_watch_video - total_not_short_video # takeout 파일 쇼츠 영상 개수

    num = 10 # 뽑아낼 상위 채널 개수 
    top_channels = get_top_channel(video_list, num)
    print(f"가장 많이 본 채널 (상위 {num}):")
    for channel, count in top_channels:
        print(f"{channel}: {count}회")
    
    # 시간 별 시청한 영상 그래프 생성
    hour_distribution = plot_hour_distribution(get_hour_distribution(video_list)[0], get_hour_distribution(video_list)[1])
    plt.show()

    # 날짜별 시청한 영상 그래프 생성
    # date_option= 분류할 기준. day, week, month 가능
    date_option = "week" # 주
    date = get_date_distribution(video_list, date_option)
    date_distribution = plot_date_distribution(date[0], date[1][1], date_option)
    plt.show()

    # 쇼츠 영상 비율 그래프 생성
    shorts_percent = draw_pie_chart(total_short_video, total_not_short_video, "short")
    plt.show()


grape_load()