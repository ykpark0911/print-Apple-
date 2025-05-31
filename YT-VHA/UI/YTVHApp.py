import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import webbrowser
from yt_api.get_yt_ob import tester_login, guest_login
from open_file.extract_video_ids import extract_video_ids_from_watch_history # 영상 id 뽑아내는 함수
from open_file.get_sub_list import get_sub_list
from open_file.json_loader import load_json # takeout 파일 여는 함수
from yt_api.get_video_info import get_video_info # 영상 정보 호출하는 함수
from yt_api.get_liked_video_info import extract_video_info_from_liked_playlist
from filter import not_short_filter # 쇼츠 영상 제외 시키는 필터 함수 
from video_statistics import make_statistics
from save_file.save_statistics import save_statistics_to_file
from grape import make_grapes, empty_grape
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class YTVHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTVH - YouTube View History Analyzer")
        self.geometry("500x300")

        # 프레임 구성
        start_page_frames = {
            0 : self.create_start_frame0(),
            1 : self.create_start_frame1(),
            2 : self.create_start_frame2()
        }

        run_page_frames = {
            0 : self.create_run_page0(),
            1 : self.create_run_page1(),
            2 : self.create_run_page2(),
            3 : self.create_run_page3()
        }

        # 페이지 구성
        self.pages = {
            "start" : start_page_frames,
            "run" : run_page_frames
        }

        # 첫 페이지 보여주기
        self.current_frame_index = 0
        self.current_page = "start"
        self.show_page("start", 0)



    def show_page(self, page, index):
        for page_dict in self.pages.values():
            for frame in page_dict.values():
                frame.pack_forget()

        self.pages[page][index].pack(expand=True, fill="both")

        self.current_frame_index = index
        self.current_page = page
    
    # name은 "shorts_distribution" 등 ...
    def show_grape(self, grape_sort, frame, include_short_or_not_key=False):
        if include_short_or_not_key:
            grape = self.grapes[grape_sort][include_short_or_not_key]
        else:
            grape = self.grapes[grape_sort]
        
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(grape, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        

    def next_page(self):
        if self.current_frame_index < len(self.pages[self.current_page].values()) - 1:
            self.current_frame_index += 1
            self.show_page(self.current_page, self.current_frame_index)
    
    def save_action(self):
        save_file_path = asksaveasfilename(
            defaultextension = ".txt",  # 기본 확장자
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")],
            title = "저장할 위치 선택"
            )
        save_statistics_to_file(self.statistics, save_file_path)
        print("저장됨")


    def guest_user_login(self):
        self.youtube = guest_login()
        self.next_page()

    def teste_user_login(self):
        self.youtube = tester_login()
        self.next_page()

    def compare_mine(self):
        self.compare_mod = "mine"
        self.next_page()
    
    def compare_friend(self):
        self.compare_mod = "friend"
        self.next_page()
    
    def file_loading(self): # 함수에서 함수 호출하는 식으로 코드 줄이기!!
        # 파일 경로 받기
        takeout_file_path = askopenfilename(
            title="테이크아웃 파일 선택",
            filetypes=[("JSON files", "*.json")]
        )
        sub_linfo_file_path = takeout_file_path[:-16] + "구독정보\\구독정보.csv"
    
        # json 파일 리스트로 변환
        self.takeout = load_json(takeout_file_path)
        # 쇼츠 영상 제외
        self.not_shorts_takeout = not_short_filter(self.takeout)
        print("테이크 아웃 파일 불러오기 완료")
        # 구독자 정보 얻기
        sub_list = get_sub_list(sub_linfo_file_path)

        # 영상 id 추출(쇼츠 제외만)
        video_ids = extract_video_ids_from_watch_history(self.not_shorts_takeout)
        print("아이디 추출 완료")

        # 영상 정보 호출(쇼츠 제외만)
        self.video_info_list = get_video_info(self.youtube, video_ids, self.not_shorts_takeout, sub_list)
        print("영상 정보 호출 완료")

        # 좋아요한 영상 정보
        self.liked_video_info_list = extract_video_info_from_liked_playlist(self.youtube)

        # 통계 자료 얻기
        self.statistics = make_statistics(self.takeout, self.not_shorts_takeout, self.video_info_list, self.liked_video_info_list)

        # 그래프 얻기
        self.grapes = make_grapes(self.statistics)

        # 디버깅 용
        print(f"불러온 영상: {len(self.video_info_list)}")
        print(f"총 추청 쇼츠 영상: {len(self.takeout) - len(self.video_info_list)}")

        self.next_button.config(state="normal")

           
    def create_start_frame0(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="YTVH (YouTube View History Analyzer)", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="게스트 사용자", command=self.guest_user_login, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="테스트 사용자", command=self.teste_user_login, width=20, height=2).pack(pady=10)
        
        return frame

    def create_start_frame1(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="비교 모드 선택", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="자신의 시청 통계 확인", command=self.compare_mine, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="친구와 비교하기", command=self.compare_friend, width=20, height=2).pack(pady=10)

        return frame

    def create_start_frame2(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="테이크아웃 파일 불러오기", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="파일 올리기", width=20, height=2, command= self.file_loading).pack(pady=5)
        link_label = tk.Label(frame, text="테이크아웃 링크 열기", fg="blue", cursor="hand2", font=("Arial", 12, "underline"))
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://takeout.google.com/"))
        self.next_button = tk.Button(frame, text="넘어가기", state="disabled", command=lambda: self.show_page("run", 0), width=20, height=2) #여기다가 pack 붙이면 변수에 None이 저장되는꼴
        self.next_button.pack(pady=20)

        return frame

    def create_run_page0(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="✅ 프로그램 실행창!", font=("Arial", 16), fg="green").pack(pady=10)

        # 오른쪽 위 저장 버튼
        tk.Button(frame, text="💾 저장하기", command=self.save_action).pack(side="right", padx=10, pady=10)
        # 중앙 버튼들
        tk.Button(frame, text="1. 통계 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 1)).pack(pady=10)
        tk.Button(frame, text="2. 좋아요 영상 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 2)).pack(pady=10)
        tk.Button(frame, text="3. 일반 영상 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 3)).pack(pady=10)

        return frame
    
    def create_run_page1(self):
        frame = tk.Frame(self)
        self.canvas = FigureCanvasTkAgg(empty_grape, master = frame)
        tk.Label(frame, text=f"통계창", font=("Arial", 20)).pack(pady=100)
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack()
        tk.Button(frame, text="쇼츠 비율", command=lambda: self.show_grape("shorts_distribution", frame)).pack()
        tk.Button(frame, text="시간 비율", command=lambda: self.show_grape("hour_distribution", frame)).pack()
        tk.Button(frame, text="날짜별 영상 개수: 일", command=lambda: self.show_grape("day_date_distribution", frame, "not_shorts")).pack()
        tk.Button(frame, text="날짜별 영상 개수: 주", command=lambda: self.show_grape("week_date_distribution", frame, "not_shorts")).pack()
        tk.Button(frame, text="날짜별 영상 개수: 달", command=lambda: self.show_grape("month_date_distribution", frame, "not_shorts")).pack()
        tk.Button(frame, text="날짜별 영상 개수: 요일", command=lambda: self.show_grape("weekDay_date_distribution", frame, "not_shorts")).pack()
        return frame
    
    def create_run_page2(self):
        frame = tk.Frame(self)
        tk.Label(frame, text=f"영상 기록 모아보기", font=("Arial", 20)).pack(pady=100)
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack()

        return frame
    
    def create_run_page3(self):
        frame = tk.Frame(self)
        tk.Label(frame, text=f"좋아요한 영상 기록 모아보기", font=("Arial", 20)).pack(pady=100)
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack()

        return frame


def YTVHApp_UI():
    app = YTVHApp()
    app.mainloop()
