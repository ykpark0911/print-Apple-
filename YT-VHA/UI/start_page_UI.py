import tkinter as tk
from tkinter.filedialog import askopenfilename
import webbrowser
from yt_api.get_yt_ob import tester_login, guest_login
from yt_api.get_like_video_info import extract_video_info_from_like_playlist
from open_file.extract_video_ids import extract_video_ids_from_watch_history # 영상 id 뽑아내는 함수
from open_file.get_sub_list import get_sub_list
from open_file.json_loader import load_json # takeout 파일 여는 함수
from yt_api.get_video_info import get_video_info, for_time_get_short_count, get_error_count #영상 정보 호출하는 함수
from filter import not_short_filter # 쇼츠 영상 제외 시키는 필터 함수 



class YTVHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTVH - YouTube View History Analyzer")
        self.geometry("500x300")
        self.pages = []
        self.current_index = 0

        # 페이지 구성
        self.pages.append(self.create_page1())
        self.pages.append(self.create_page2())
        self.pages.append(self.create_page3())
        self.pages.append(self.create_final_page())

        # 첫 페이지 보여주기
        self.show_page(0)

    def show_page(self, index):
        for page in self.pages:
            page.pack_forget()
        self.pages[index].pack(expand=True, fill="both")
        self.current_index = index

    def next_page(self):
        if self.current_index < len(self.pages) - 1:
            self.show_page(self.current_index + 1)
    
    def statistics_mod(self):
        self.mod= 1
        self.next_page()
    
    def compare_mod(self):
        self.mod= 2
        self.next_page()


    def guest_user_login(self):
        self.youtube = guest_login()
        self.next_page()

    def tester_user_login(self):
        self.youtube = tester_login()
        self.like_list= extract_video_info_from_like_playlist(self.youtube)
        self.next_page()
    
    def file_loading(self): # 함수에서 함수 호출하는 식으로 코드 줄이기!!
        takeout_file_path = askopenfilename(
            title="테이크아웃 파일 선택",
            filetypes=[("JSON files", "*.json")]
        )
        if takeout_file_path:
            print("파일 경로:", takeout_file_path)  # ✅ 경로가 콘솔에 출력됨

        sub_linfo_path = takeout_file_path[:-16] + "구독정보\\구독정보.csv"
        sub_list = get_sub_list(sub_linfo_path)
       
        # json 파일 리스트로 변환
        video_list= load_json(takeout_file_path)
        print("테이크 아웃 파일 불러오기 완료")

        # 쇼츠 영상 제외
        self.not_short_video_list= not_short_filter(video_list)
        self.total_watch_video = len(video_list) # takeout 파일 총 영상 개수
        self.total_not_short_video1 = len(self.not_short_video_list) # takeout 파일 쇼츠 제외한 영상 개수
        total_short_video = self.total_watch_video - self.total_not_short_video1 # takeout 파일 쇼츠 영상 개수

        # 영상 id 추출
        video_ids= extract_video_ids_from_watch_history(self.not_short_video_list)
        print("아이디 추출 완료")

        # 영상 정보 호출
        self.video_info_list= get_video_info(self.youtube, video_ids, self.not_short_video_list, sub_list)
        print("영상 정보 호출 완료")

        self.total_not_short_video2 = len(self.not_short_video_list) # 쇼츠 제외 영상 개수
        self.total_short_video2 = total_short_video + for_time_get_short_count() # 쇼츠 영상 개수
        self.error_video = get_error_count() # 에러 영상 개수

        print(f"불러온 영상: {self.total_watch_video}")
        print(f"추정 쇼츠 제외 영상: {self.total_not_short_video2}, 총 추청 쇼츠 영상: {self.total_short_video2}")
        print(f"오류 영상: {self.error_video}")

        self.next_button.config(state="normal")
        self.frieds_file_upload_button(state="normal")
           
    def create_page1(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="YTVH (YouTube View History Analyzer)", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="게스트 사용자", command=self.guest_user_login, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="테스트 사용자", command=self.tester_user_login, width=20, height=2).pack(pady=10)
        
        return frame

    def create_page2(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="비교 모드 선택", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="자신의 시청 통계 확인", command=self.next_page, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="친구와 비교하기", command=self.next_page, width=20, height=2).pack(pady=10)
        return frame

    def create_page3(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="테이크아웃 파일 불러오기", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="파일 올리기", width=20, height=2, command= self.file_loading).pack(pady=5)
        self.frieds_file_upload_button = tk.Button(frame, text="파일 올리기: 친구 파일", state="disabled", width=20, height=2, command= self.file_loading)
        self.frieds_file_upload_button.pack(pady=20)
        link = tk.Label(frame, text="테이크아웃 링크 열기", fg="blue", cursor="hand2", font=("Arial", 12, "underline"))
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://takeout.google.com/"))

        self.next_button = tk.Button(frame, text="넘어가기", state="disabled", command=self.next_page, width=20, height=2) #여기다가 pack 붙이면 변수에 None이 저장되는꼴
        self.next_button.pack(pady=20)       

        return frame

    def create_final_page(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="✅ 프로그램 실행창!", font=("Arial", 20), fg="green").pack(pady=100)
        return frame



def start_UI():
    app = YTVHApp()
    app.mainloop()
