import pandas as pd #pip install pandas


def load_sub_file(csv_path):
    data = pd.read_csv(csv_path, encoding='utf-8-sig')

    # .to_dict: csv를 딕셔너리로 불러옴
    # orient = 'records': 각 행 기준
    sub_info_list = data.to_dict(orient='records')

    # 구독한 채널 이름 목록을 담을 리스트
    sub_list = []

    for channel in sub_info_list:
        name = channel.get('채널 제목')
        sub_list.append(name)

    return sub_list


'''
["달이쌤", "Cobblemon", "마소의 마크일기"]
'''