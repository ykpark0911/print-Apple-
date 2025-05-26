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
    ax.set_xlabel("Watching Time (h)")
    ax.set_ylabel("Number of video views")
    ax.set_title("Viewing distribution by time zone")
    ax.set_xticks(hours)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    return fig


def plot_date_distribution(dates, counts):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, counts, marker='o', linestyle='-', color='green')
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of videos watched")
    ax.set_title("Distribution of videos viewed by date")
    plt.xticks(rotation=45)  # 간단하게 회전만 지정
    ax.grid(True, linestyle='--', alpha=0.7)

    return fig

def plot_date_distribution(dates, counts, title_suffix):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, counts, marker='o', linestyle='-', color='green')
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of videos watched")
    ax.set_title(f"Distribution of videos viewed by {title_suffix}")
    plt.xticks(rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig




def plot_category_distribution(categories, counts):
    """
    카테고리별 시청 분포를 시각화

    Parameters:
        categories (list): 카테고리 이름 리스트
        counts (list): 카테고리별 시청 횟수
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(categories, counts, color='orchid')
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of videos watched")
    ax.set_title("Distribution of videos viewed by category")
    plt.xticks(rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    return fig