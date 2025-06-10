import json
import matplotlib.pyplot as plt

def save_all_data_to_json_file(statistics_dict, sub_list, liked_video_info_list, video_info_list, save_path):
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


def save_grape(save_path, grape_data, grape_name):
    grape_data.tight_layout()
    full_file_path = save_path + grape_name + ".png"
    grape_data.savefig(full_file_path, dpi=200, bbox_inches='tight')


def save_all_grape(grapes, save_path):
    for key, value in grapes.items():
    # 값이 딕셔너리인지 확인합니다.
        if isinstance(value, dict): #어떤 객체가 특정 클래스(또는 자료형)의 인스턴스(객체)인지 확인할 때 사용
        # 중첩된 딕셔너리 내부의 키-값 쌍을 순회합니다.
            for sub_key, sub_value in value.items():
                graph_data = sub_value
                graph_name = f"{key}_{sub_key}" # 그래프 파일명 등에 사용할 이름
                save_grape(save_path, graph_data, graph_name)
        else:
        # 딕셔너리가 아닌 단일 값인 경우
            graph_data = value
            graph_name = key # 그래프 파일명 등에 사용할 이름
            save_grape(save_path, graph_data, graph_name)

    print("✅ 모든 데이터 저장 완료:", save_path)