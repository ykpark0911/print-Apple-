import json

def save_all_data_to_file(statistics_dict, sub_list, liked_video_info_list, video_info_list, save_path):
    # 모든 데이터를 담을 하나의 딕셔너리 생성
    all_data = {
        "statistics": statistics_dict,
        "sub_list": sub_list,
        "liked_video_info_list": liked_video_info_list,
        "video_info_list": video_info_list
    }

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("✅ 모든 데이터 저장 완료:", save_path)