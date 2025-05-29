import pandas as pd #pip install pandas


def get_sub_list(csv_path):
    data = pd.read_csv(csv_path, encoding='utf-8-sig')

    sub_list = []

    sub_info_list = data.to_dict(orient='records') #orient 옵션에서 'records'는 각 행을 딕셔너리로, 전체는 리스트로 저장

    for channel in sub_info_list:
        name = channel.get('채널 제목')
        sub_list.append(name)

    return sub_list

'''
{'채널 ID': 'UC-Jp4WHCXhxvWQ5Ab4JibJQ', '채널 URL': 'http://www.youtube.com/channel/UC-Jp4WHCXhxvWQ5Ab4JibJQ', '채널 제목': '벙
구'}
'''