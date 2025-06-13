#  ── 그래프 만드는 모듈 ──

import matplotlib.pyplot as plt

def draw_pie_chart(count1, count2, sort):
    labels = [sort, f'Not {sort}']
    sizes = [count1, count2]
    colors = ['#ff9999', '#66b3ff']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')  # 원형 유지

    return fig


def plot_hour_distribution(hours, counts):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(hours, counts, color='skyblue')
    ax.set_xlabel("시간")
    ax.set_ylabel("시청 횟수")
    ax.set_title("시간별 시청 횟수 분포")
    ax.set_xticks(hours)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    return fig

def plot_date_distribution(dates, counts, title_suffix):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(dates, counts, marker='o', linestyle='-', color='green')
    ax.set_ylabel("시청 횟수")
    ax.set_title(f"\"{title_suffix}\" 기준으로 한 날짜별 시청 횟수")
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig


def plot_category_distribution(categories, counts):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(categories, counts, color='orchid')
    ax.set_xlabel("카테고리")
    ax.set_ylabel("시청 횟수")
    ax.set_title("카테고리 별 시청 횟수")
    plt.xticks(rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    return fig


def make_grapes(statistics):
    shorts_distribution_dict = statistics["shorts_distribution"]
    shorts_percentage_grape = draw_pie_chart(shorts_distribution_dict["total_takeout"], shorts_distribution_dict["total_not_shorts_takeout"], "short")

    hour_distribution_dict = statistics["hour_distribution"]
    hour_distribution_grape = plot_hour_distribution(hour_distribution_dict["include_shorts"]["hours"], hour_distribution_dict["include_shorts"]["counts"])

    # 일간 분포
    day_date_distribution_dict = statistics["day_date_distribution"]
    include_shorts_day_date_distribution_grape = plot_date_distribution(day_date_distribution_dict["include_shorts"]["day_dates"], day_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 일")
    not_shorts_day_date_distribution_grape = plot_date_distribution(day_date_distribution_dict["not_shorts"]["day_dates"], day_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 일")

    # 주간 분포
    week_date_distribution_dict = statistics["week_date_distribution"]
    include_shorts_week_date_distribution_grape = plot_date_distribution(week_date_distribution_dict["include_shorts"]["week_dates"], week_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 주")
    not_shorts_week_date_distribution_grape = plot_date_distribution(week_date_distribution_dict["not_shorts"]["week_dates"], week_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 주")

    # 월간 분포
    month_date_distribution_dict = statistics["month_date_distribution"]
    include_shorts_month_date_distribution_grape = plot_date_distribution(month_date_distribution_dict["include_shorts"]["month_dates"], month_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 달")
    not_shorts_month_date_distribution_grape = plot_date_distribution(month_date_distribution_dict["not_shorts"]["month_dates"], month_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 달")

    # 평균 주간 분포
    average_week_date_distribution_dict = statistics["average_week_date_distribution"]
    include_shorts_average_week_date_distribution_grape = plot_date_distribution(average_week_date_distribution_dict["include_shorts"]["average_week_dates"], average_week_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 주(평균)")
    not_shorts_average_week_date_distribution_grape = plot_date_distribution(average_week_date_distribution_dict["not_shorts"]["average_week_dates"], average_week_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 주(평균)")

    # 평균 월간 분포
    average_month_date_distribution_dict = statistics["average_month_date_distribution"]
    include_shorts_average_month_date_distribution_grape = plot_date_distribution(average_month_date_distribution_dict["include_shorts"]["average_month_dates"], average_month_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 달(평균)")
    not_shorts_average_month_date_distribution_grape = plot_date_distribution(average_month_date_distribution_dict["not_shorts"]["average_month_dates"], average_month_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 달(평균)")

    # 요일별 분포
    weekDay_date_distribution_dict = statistics["weekDay_date_distribution"]
    include_shorts_weekDay_date_distribution_grape = plot_date_distribution(weekDay_date_distribution_dict["include_shorts"]["weekDay_dates"], weekDay_date_distribution_dict["include_shorts"]["counts"], "(쇼츠 포함한) 요일")
    not_shorts_weekDay_date_distribution_grape = plot_date_distribution(weekDay_date_distribution_dict["not_shorts"]["weekDay_dates"], weekDay_date_distribution_dict["not_shorts"]["counts"], "(쇼츠 제외한) 요일")

    # 카테고리별 분포
    category_distribution_dict = statistics["category_distribution"]
    category_distribution_grape = plot_category_distribution(category_distribution_dict["categories"], category_distribution_dict["counts"])

    # 최종 결과 딕셔너리
    statistics_grape = {
        "shorts_distribution" : shorts_percentage_grape,
        "hour_distribution" : hour_distribution_grape,
        "day_date_distribution": {
            "include_shorts": include_shorts_day_date_distribution_grape,
            "not_shorts": not_shorts_day_date_distribution_grape
        },
        "week_date_distribution": {
            "include_shorts": include_shorts_week_date_distribution_grape,
            "not_shorts": not_shorts_week_date_distribution_grape
        },
        "month_date_distribution": {
            "include_shorts": include_shorts_month_date_distribution_grape,
            "not_shorts": not_shorts_month_date_distribution_grape
        },
        "average_week_date_distribution": {
            "include_shorts": include_shorts_average_week_date_distribution_grape,
            "not_shorts": not_shorts_average_week_date_distribution_grape
        },
        "average_month_date_distribution": {
            "include_shorts": include_shorts_average_month_date_distribution_grape,
            "not_shorts": not_shorts_average_month_date_distribution_grape
        },
        "weekDay_date_distribution": {
            "include_shorts": include_shorts_weekDay_date_distribution_grape,
            "not_shorts": not_shorts_weekDay_date_distribution_grape
        },
        "category_distribution" : category_distribution_grape
    }

    return statistics_grape


def make_compare_grapes(statistics):
    shorts_distribution_dict = statistics["shorts_distribution"]
    shorts_percentage_grape = draw_pie_chart(shorts_distribution_dict["total_takeout"], shorts_distribution_dict["total_not_shorts_takeout"], "short")

    hour_distribution_dict = statistics["hour_distribution"]
    hour_distribution_grape = plot_hour_distribution(hour_distribution_dict["include_shorts"]["hours"], hour_distribution_dict["include_shorts"]["counts"])

    # 일간 분포
    day_date_distribution_dict = statistics["day_date_distribution"]
    include_shorts_day_date_distribution_grape = plot_date_distribution(day_date_distribution_dict["include_shorts"]["day_dates"], day_date_distribution_dict["include_shorts"]["counts"], "day")
    not_shorts_day_date_distribution_grape = plot_date_distribution(day_date_distribution_dict["not_shorts"]["day_dates"], day_date_distribution_dict["not_shorts"]["counts"], "day")

    # 주간 분포
    week_date_distribution_dict = statistics["week_date_distribution"]
    include_shorts_week_date_distribution_grape = plot_date_distribution(week_date_distribution_dict["include_shorts"]["week_dates"], week_date_distribution_dict["include_shorts"]["counts"], "week")
    not_shorts_week_date_distribution_grape = plot_date_distribution(week_date_distribution_dict["not_shorts"]["week_dates"], week_date_distribution_dict["not_shorts"]["counts"], "week")

    # 월간 분포
    month_date_distribution_dict = statistics["month_date_distribution"]
    include_shorts_month_date_distribution_grape = plot_date_distribution(month_date_distribution_dict["include_shorts"]["month_dates"], month_date_distribution_dict["include_shorts"]["counts"], "month")
    not_shorts_month_date_distribution_grape = plot_date_distribution(month_date_distribution_dict["not_shorts"]["month_dates"], month_date_distribution_dict["not_shorts"]["counts"], "month")

    # 평균 주간 분포
    average_week_date_distribution_dict = statistics["average_week_date_distribution"]
    include_shorts_average_week_date_distribution_grape = plot_date_distribution(average_week_date_distribution_dict["include_shorts"]["average_week_dates"], average_week_date_distribution_dict["include_shorts"]["counts"], "week (avg)")
    not_shorts_average_week_date_distribution_grape = plot_date_distribution(average_week_date_distribution_dict["not_shorts"]["average_week_dates"], average_week_date_distribution_dict["not_shorts"]["counts"], "week (avg)")

    # 평균 월간 분포
    average_month_date_distribution_dict = statistics["average_month_date_distribution"]
    include_shorts_average_month_date_distribution_grape = plot_date_distribution(average_month_date_distribution_dict["include_shorts"]["average_month_dates"], average_month_date_distribution_dict["include_shorts"]["counts"], "month (avg)")
    not_shorts_average_month_date_distribution_grape = plot_date_distribution(average_month_date_distribution_dict["not_shorts"]["average_month_dates"], average_month_date_distribution_dict["not_shorts"]["counts"], "month (avg)")

    # 요일별 분포
    weekDay_date_distribution_dict = statistics["weekDay_date_distribution"]
    include_shorts_weekDay_date_distribution_grape = plot_date_distribution(weekDay_date_distribution_dict["include_shorts"]["weekDay_dates"], weekDay_date_distribution_dict["include_shorts"]["counts"], "weekDay")
    not_shorts_weekDay_date_distribution_grape = plot_date_distribution(weekDay_date_distribution_dict["not_shorts"]["weekDay_dates"], weekDay_date_distribution_dict["not_shorts"]["counts"], "weekDay")

    category_distribution_dict = statistics["category_distribution"]
    category_distribution_grape = plot_category_distribution(category_distribution_dict["categories"], category_distribution_dict["counts"])

    # 최종 결과 딕셔너리
    statistics_grape = {
        "shorts_distribution" : shorts_percentage_grape,
        "hour_distribution" : hour_distribution_grape,
        "day_date_distribution": {
            "include_shorts": include_shorts_day_date_distribution_grape,
            "not_shorts": not_shorts_day_date_distribution_grape
        },
        "week_date_distribution": {
            "include_shorts": include_shorts_week_date_distribution_grape,
            "not_shorts": not_shorts_week_date_distribution_grape
        },
        "month_date_distribution": {
            "include_shorts": include_shorts_month_date_distribution_grape,
            "not_shorts": not_shorts_month_date_distribution_grape
        },
        "average_week_date_distribution": {
            "include_shorts": include_shorts_average_week_date_distribution_grape,
            "not_shorts": not_shorts_average_week_date_distribution_grape
        },
        "average_month_date_distribution": {
            "include_shorts": include_shorts_average_month_date_distribution_grape,
            "not_shorts": not_shorts_average_month_date_distribution_grape
        },
        "weekDay_date_distribution": {
            "include_shorts": include_shorts_weekDay_date_distribution_grape,
            "not_shorts": not_shorts_weekDay_date_distribution_grape
        },
        "category_distribution" : category_distribution_grape
    }

    return statistics_grape


def make_text(statistics):
    """
    주어진 통계 데이터를 기반으로 채널 통계 텍스트를 생성하여 반환합니다.
    """
    text_content = "--- 영상 가장 많이 본 채널 상위 10개 ---\n"
    if "top_channel" in statistics:
        for i, (channel, count) in enumerate(statistics["top_channel"][:10]):
            text_content += f"{i+1}. {channel}: {count}회\n"
    else:
        text_content += "데이터 없음\n"

    text_content += "\n--- 좋아요한 영상 중 가장 많이 본 채널 상위 10개 ---\n"
    # JSON 데이터의 오타 'channe'를 확인하고 사용합니다.
    if "top_liked_channe" in statistics:
        for i, (channel, count) in enumerate(statistics["top_liked_channe"][:10]):
            text_content += f"{i+1}. {channel}: {count}회\n"
    else:
        text_content += "데이터 없음\n"

    return text_content
 
