# 그래프 그리기
import matplotlib.pyplot as plt # 그래프 그릴 수 있게 해주는 라이브러리 #pip install matplotlib
from open_file.json_loader import load_json # takeout 파일 여는 함수
from video_statistics import make_statistics # 영상 통계내는 함수
from grape import plot_hour_distribution, plot_date_distribution, draw_pie_chart # 그래프 만드는 함수
from filter import not_short_filter # 쇼츠 영상 제외 시키는 필터 함수 


def grape_load():
    # takeout 파일 경로
    path = "C:\\pypy\\print-Apple-\\YT-VHA\\open_file\\Takeout\\YouTube 및 YouTube Music\\시청 기록\\시청 기록.json"

    # json 파일 리스트로 변환
    takeout= load_json(path)
    print("테이크 아웃 파일 불러오기 완료")
    
    # 쇼츠 영상 제외
    not_short_takeout = not_short_filter(takeout)

    

    takeout_statistics = make_statistics(takeout, not_short_takeout, video_info_list, like_list)
    print(takeout_statistics)


    top_channels = takeout_statistics["top_channel"]
    print(f"가장 많이 본 채널 (상위 10):")
    for channel, count in top_channels:
        print(f"{channel}: {count}회")


    # 시간 별 시청한 영상 그래프 생성
    hour_distribution = takeout_statistics["top_channel"]
    hour_distribution_grape = plot_hour_distribution(hour_distribution["hours"], hour_distribution["counts"])
    plt.show()

    # 날짜별 시청한 영상 그래프 생성
    # date_option= 분류할 기준. day, week, month 가능
    date_distribution = takeout_statistics["week_date_distribution"]
    date_distribution_grape = plot_date_distribution(date_distribution["week_dates"], date_distribution["week_counts"], "week")
    plt.show()

    # 쇼츠 영상 비율 그래프 생성
    shorts_distribution = takeout_statistics["shorts_distribution"]
    shorts_percent = draw_pie_chart(shorts_distribution["total_takeout"], shorts_distribution["total_sohrts_takeout"],  "short")
    plt.show()


grape_load()