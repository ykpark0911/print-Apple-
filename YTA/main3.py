# 구독자 정보 불러오기
from open_file.get_sub_list import get_sub_list



def sub_load():
    path = "C:\\pypy\\YTA-file\\YTA\\open_file\\Takeout\\YouTube 및 YouTube Music\\구독정보\\구독정보.csv"
    sub_list = get_sub_list(path)
    print(sub_list)

    return sub_list

sub_load()

