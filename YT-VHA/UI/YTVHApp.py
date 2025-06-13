import tkinter as tk
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import webbrowser
from yt_api.get_yt_ob import tester_login, guest_login
from open_file.extract_video_ids import extract_video_ids # 영상 id 뽑아내는 함수
from open_file.get_sub_list import load_sub_file
from open_file.json_loader import load_takeout_file, load_save_file # takeout 파일 여는 함수 
from yt_api.get_video_info import call_video_info # 영상 정보 호출하는 함수
from yt_api.get_liked_video_info import extract_video_info_from_liked_playlist
from filter import * # 쇼츠 영상 제외 시키는 필터 함수 
from video_statistics import make_statistics
from save_file import save_all_data_to_json_file, save_all_grape
from grape import make_grapes, make_text
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tool import dateTime_iso8601_to_dateTime

import matplotlib.pyplot as plt
plt.rc('font', family='Malgun Gothic')


class YTVHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTVH - YouTube View History Analyzer")
        self.geometry("1800x900")

        # 각종 변수 초기화
        # 영상 관련 리스트 초기화
        self.video_info_list = []
        self.sub_list= []
        self.liked_video_info_list = []

        # 통계용 변수 초기화
        self.include_shorts = tk.StringVar(value= "not_shorts") # 쇼츠 포함, 미포함
        self.current_grape = None
                
        # 필터링 관련 변수 초기화
        self.subscribed_only_var = tk.BooleanVar(value=False) # 구독 여부 필터용
        self.selected_date_entry = None # 날짜 필터용
        self.selected_channel_entry = None # 채널 필터용
        self.selected_category_var = tk.StringVar(value="none") # 카테고리 필터용
        self.selected_platform_var = tk.StringVar(value="YouTube") # 플렛폼 필터용
        self.selected_channel_var = tk.StringVar(value="<전체>") # 좋아요 영상 필터용
        self.selected_video_sort_var = tk.StringVar(value="<전체>") # 쇼츠 필터용
        self.sort_options = ["최신순", "오래된 순", "랜덤"] #정렬 필터에 들어갈 목록

        # 영상 보여주기 페이지 초기화
        self.video_display_container_frame_run2 = None 
        self.video_canvas_run2 = None                 
        self.video_display_scrollbar_run2 = None
        self.video_scrollable_frame_run2 = None
        self.stats_text_widget = None
        self.filter_frame_for_run2 = None # 필터 프레임

        self.video_display_container_frame_run3 = None 
        self.video_canvas_run3 = None                 
        self.video_display_scrollbar_run3 = None
        self.video_scrollable_frame_run3 = None
        self.filter_frame_for_run3 = None # 필터 프레임
        self.subscribed_channels_radio_frame = None # 구독 채널 라디오 버튼용 프레임

        self.current_video_page = 0    # 현재 비디오 페이지
        self.videos_per_page = 5       # 한 페이지에 보여줄 영상 개수
        self.total_filtered_videos = [] # 현재 필터링된 전체 영상 목록
        self.placeholder_img = ImageTk.PhotoImage(Image.new("RGB", (120, 90), color = 'gray')) # 이미지 없을 때, 사용할 대체 이미지

        # 시작 페이지 생성
        self.make_start_frame()

        # 첫 페이지 보여주기
        self.current_frame_index = 0
        self.current_page = "start"
        self.show_page("start", 0)



# 페이지 프레임 만드는 함수
    def make_start_frame(self):
        # 시작 프레임 구성
        start_page_frames = {
            0 : self.create_start_frame0(),
            1 : self.create_start_frame1(),
        }
        # 시작 페이지 추가
        self.pages = {"start" : start_page_frames}


    def make_run_frame(self):
        if self.video_info_list != []: # 파일 업로드 성공
            # 다음 페이지로 넘어갈 수 있도록 버튼 상태 변경
            self.next_button.config(state="normal")
            self.takeout_upload_button.config(state="disabled")
            self.save_file_upload_button.config(state="disabled")

            # 실행 프레임 구성
            run_page_frames = {
                0 : self.create_run_page0(),
                1 : self.create_run_page1(),
                2 : self.create_run_page2(),
            }
            if self.authority == "tester":
                run_page_frames[3] = self.create_run_page3()
    
            # 시작 페이지 추가
            self.pages["run"] = run_page_frames
            
        else:
            print("파일 오류")



# 각 페이지 만드는 함수
    def create_start_frame0(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="YTVH (YouTube View History Analyzer)", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="게스트 사용자", command=self.guest_user_login, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="테스트 사용자", command=self.teste_user_login, width=20, height=2).pack(pady=10)
        
        return frame


    def create_start_frame1(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="테이크아웃 파일 불러오기", font=("Arial", 16)).pack(pady=20)
        self.takeout_upload_button = tk.Button(frame, text="시청 기록.json 파일 올리기", width=20, height=2, command= self.file_loading)
        self.takeout_upload_button.pack(pady=5)
        self.save_file_upload_button = tk.Button(frame, text="save_file.json 파일 올리기", width=20, height=2, command= self.save_file_loading)
        self.save_file_upload_button.pack(pady=5)
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
        tk.Button(frame, text="💾 JSON 파일로 분석 데이터 저장하기", command=self.save_file).pack(padx=10, pady=10)
        tk.Button(frame, text="💾 통계 그래프 사진으로 저장하기", command=self.save_grape_file).pack(padx=10, pady=10)
        
        # 중앙 버튼들
        tk.Button(frame, text="1. 통계 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 1)).pack(pady=10)
        tk.Button(frame, text="2. 일반 영상 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 2)).pack(pady=10)
        if self.authority == "tester":
            liked_video_button_state = "normal"
        else:
            liked_video_button_state = "disabled"
        tk.Button(frame, text="3. 좋아요 영상 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 3),
                  state=liked_video_button_state).pack(pady=10)

        return frame

 
    def create_run_page1(self):
        frame = tk.Frame(self) # 전체 페이지를 담을 메인 프레임

        # --- 왼쪽 컬럼: 통계 종류 선택 버튼들 ---
        stats_filter_frame = tk.Frame(frame, bd=2, relief="groove", width=200)
        stats_filter_frame.pack(side="left", fill="y", padx=10, pady=10)
        stats_filter_frame.pack_propagate(False) # 프레임 크기가 내용에 따라 늘어나지 않도록 고정

        tk.Label(stats_filter_frame, text="통계 종류", font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Radiobutton(stats_filter_frame, text= "쇼츠 영상 포함", variable= self.include_shorts, value="include_shorts", command= lambda: self.show_grape(self.current_grape, self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Radiobutton(stats_filter_frame, text= "쇼츠 영상 제외", variable= self.include_shorts, value="not_shorts", command= lambda: self.show_grape(self.current_grape, self.graph_display_frame)).pack(fill="x", padx=5, pady=5)

        # 각 통계 버튼을 왼쪽 필터 프레임에 배치
        tk.Button(stats_filter_frame, text="채널 통계 보기", command=self.show_text).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="쇼츠 비율", command=lambda: self.show_grape("shorts_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="카테고리별 비율", command=lambda: self.show_grape("category_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="시간 비율", command=lambda: self.show_grape("hour_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="날짜별 영상 개수: 일", command=lambda: self.show_grape("day_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="날짜별 영상 개수: 주", command=lambda: self.show_grape("week_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="날짜별 영상 개수: 달", command=lambda: self.show_grape("month_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="날짜별 영상 개수: 요일", command=lambda: self.show_grape("weekDay_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="하루 평균 날짜별 영상 개수: 주", command=lambda: self.show_grape("average_week_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)
        tk.Button(stats_filter_frame, text="하루 평균 날짜별 영상 개수: 달", command=lambda: self.show_grape("average_month_date_distribution", self.graph_display_frame)).pack(fill="x", padx=5, pady=5)




        # --- 오른쪽 컬럼: 그래프 표시 영역 ---
        self.graph_display_frame = tk.Frame(frame)
        self.graph_display_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.stats_text_widget = tk.Text(self.graph_display_frame, wrap="word", state="disabled", font=("Arial", 12))

        # 뒤로가기 버튼은 메인 프레임의 바닥에 배치
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack(side="bottom", pady=10)

        return frame
    

    def create_run_page2(self):
        frame = tk.Frame(self)
        # **[1] 좌측 필터 프레임과 우측 영상 표시 컨테이너 프레임을 나눕니다.**
        # `side="left"`와 `side="right"`를 사용하여 좌우로 배치합니다.
        filter_frame = tk.Frame(frame, bd=2, relief="groove", width=200) # 필터링 영역 (테두리 및 고정 너비)
        filter_frame.pack(side="left", fill="y", padx=10, pady=10) # y축으로 채우기
        filter_frame.pack_propagate(False) # 이 프레임의 크기가 자식 위젯에 의해 변경되지 않도록 고정

        video_display_container_frame = tk.Frame(frame) # 비디오 목록을 담을 컨테이너
        video_display_container_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10) # 남은 공간을 모두 채우고 확장 가능하게

        # --- 왼쪽 컬럼: 필터링 옵션 ---
        tk.Label(filter_frame, text="필터링 옵션", font=("Arial", 12, "bold")).pack(pady=5)

        # 정렬 기준
        tk.Label(filter_frame, text="정렬 기준:").pack(anchor="w", padx=5, pady=(5, 2))
        self.sort_combobox = ttk.Combobox(
            filter_frame,
            values=self.sort_options,
            state="readonly"
        )
        self.sort_combobox.set(self.sort_options[0]) # '최신순'으로 초기 설정
        self.sort_combobox.pack(fill="x", padx=5, pady=5)

        # 1. 구독한 채널 필터 (체크박스)
        tk.Checkbutton(filter_frame, text="구독한 채널만 보기", variable=self.subscribed_only_var).pack(anchor="w", padx=5, pady=2)
        
        # 2. 선택한 날짜 필터 (입력 필드)
        tk.Label(filter_frame, text="날짜 선택 (YYYY-MM-DD):").pack(anchor="w", padx=5, pady=1)
        self.selected_date_entry = tk.Entry(filter_frame)
        self.selected_date_entry.pack(fill="x", padx=5, pady=2)

        # 3. 선택한 채널 필터 (입력 필드)
        tk.Label(filter_frame, text="채널 이름 입력:").pack(anchor="w", padx=5, pady=1)
        self.selected_channel_entry = tk.Entry(filter_frame)
        self.selected_channel_entry.pack(fill="x", padx=5, pady=2)


        # 4. 선택한 카테고리 필터 (라디오 버튼)
        tk.Label(filter_frame, text="카테고리 선택:").pack(anchor="w", padx=5, pady=2)
        self.categories = [
            "none",
            "Film & Animation",
            "Autos & Vehicles",
            "Music",
            "Pets & Animals",
            "Sports",
            "Gaming",
            "People & Blogs",
            "Comedy",
            "Entertainment",
            "News & Politics",
            "Howto & Style",
            "Education",
            "Science & Technology"
        ]
        for category_name in self.categories:
            tk.Radiobutton(filter_frame, text=category_name, variable=self.selected_category_var, value=category_name).pack(anchor="w", padx=5)

        # 5. 플랫폼 필터 (라디오 버튼)
        tk.Label(filter_frame, text="플랫폼 선택:").pack(anchor="w", padx=5, pady=5)

        tk.Radiobutton(filter_frame, text="YouTube", variable=self.selected_platform_var, value="YouTube").pack(anchor="w", padx=5)

        tk.Radiobutton(filter_frame, text="YouTube Music", variable=self.selected_platform_var, value="YouTube Music").pack(anchor="w", padx=5)
        
        # --- 완료 버튼 (모든 필터 설정을 적용) ---
        tk.Button(filter_frame, text="필터 적용", command=self.apply_video_filter1).pack(anchor="w", padx=5, pady=10, fill="x")
        
        # --- 오른쪽 컬럼: 비디오 표시 영역 및 페이지네이션 컨트롤 ---
        self.create_video_display_widgets(frame, 'run2')

        # 뒤로가기 버튼은 맨 아래에 배치
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack(side="bottom", pady=10)

        return frame
    

    def create_run_page3(self):
        frame = tk.Frame(self)

        filter_frame = tk.Frame(frame, bd=2, relief="groove", width=200)
        filter_frame.pack(side="left", fill="y", padx=10, pady=10)
        filter_frame.pack_propagate(False)

        video_display_container_frame = tk.Frame(frame)
        video_display_container_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # --- 왼쪽 컬럼: 필터링 옵션 ---
        tk.Label(filter_frame, text="필터링 옵션", font=("Arial", 12, "bold")).pack(pady=10)

        self.sort_combobox.set(self.sort_options[0]) # '최신순'으로 초기 설정
        self.sort_combobox.pack(fill="x", padx=5, pady=5)

        tk.Label(filter_frame, text="채널 선택:").pack(anchor="w", padx=5, pady=2)
        for channel_name in self.sub_list:
            tk.Radiobutton(filter_frame, text=channel_name, variable=self.selected_channel_var , value=channel_name).pack(anchor="w", padx=5, pady=1)

        # 쇼츠 필터 (라디오 버튼)
        tk.Label(filter_frame, text="쇼츠 또는 일반 영상 선택:").pack(anchor="w", padx=5, pady=10)
        tk.Radiobutton(filter_frame, text="not shorts", variable=self.selected_video_sort_var, value="not shorts").pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(filter_frame, text="shorts", variable=self.selected_video_sort_var, value="shorts").pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(filter_frame, text="<전체>", variable=self.selected_video_sort_var, value="<전체>").pack(anchor="w", padx=5, pady=2)

        # --- 완료 버튼 (모든 필터 설정을 적용) ---
        tk.Button(filter_frame, text="필터 적용", command=self.apply_video_filter2).pack(anchor="w", padx=5, pady=15, fill="x")

       # 우측 비디오 표시 컨테이너 (공통 함수로 생성)
        self.create_video_display_widgets(frame, 'run3')

        # 뒤로가기 버튼은 맨 아래에 배치
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack(side="bottom", pady=10)

        return frame



# 페이지 내용 띄우는 함수
    def show_page(self, page, index):
        # 모든 페이지 프레임을 숨김
        for page_group in self.pages.values():
            for frame_item in page_group.values():
                frame_item.pack_forget()

        # 현재 페이지의 프레임을 보여줌
        self.pages[page][index].pack(expand=True, fill="both")

        # 현재 프레임과, 페이지
        self.current_frame_index = index
        self.current_page = page

        # run 페이지인 경우에는 
        if page == "run":
            # 모든 필터 프레임 숨김
            if self.filter_frame_for_run2: self.filter_frame_for_run2.pack_forget()
            if self.filter_frame_for_run3: self.filter_frame_for_run3.pack_forget()

            self.pagination_reset()    


    def show_grape(self, grape_sort, parent_frame):
        self.current_grape = grape_sort

        if self.stats_text_widget and self.stats_text_widget.winfo_ismapped():
            self.stats_text_widget.pack_forget()
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()


        if grape_sort in ["shorts_distribution", "hour_distribution", "category_distribution"]:
            grape = self.grapes[grape_sort]
        else:     
            grape = self.grapes[grape_sort][self.include_shorts.get()]

        self.canvas = FigureCanvasTkAgg(grape, master=parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 100))
    

    def show_text(self):
        # 현재 보이는 그래프 캔버스를 숨김.
        if hasattr(self, "canvas") and self.canvas.get_tk_widget().winfo_ismapped():
            self.canvas.get_tk_widget().pack_forget()

        # 텍스트 위젯을 보이게 합니다.
        if self.stats_text_widget:
            self.stats_text_widget.pack(fill="both", expand=True)
            
            # 텍스트 위젯 내용을 업데이트합니다.
            self.stats_text_widget.config(state="normal") # 쓰기 가능하도록 변경
            self.stats_text_widget.delete("1.0", tk.END) # 기존 내용 삭제

            # 수정: grape.py의 make_text 함수를 호출하여 텍스트 내용을 가져옵니다.
            self.stats_text_widget.insert(tk.END, self.text_content)
            self.stats_text_widget.config(state="disabled") # 다시 읽기 전용으로 변경



# 페이지네이션 관련 함수
    def pagination_reset(self):
        if self.current_frame_index == 2: # 일반 영상 보기 페이지
        # 페이지네이션 버튼 및 라벨이 해당 페이지의 것으로 참조
            self.prev_page_button = self.prev_page_button_run2
            self.next_page_button = self.next_page_button_run2
            self.page_info_label = self.page_info_label_run2
            self.video_canvas = self.video_canvas_run2
            self.video_scrollable_frame = self.video_scrollable_frame_run2
            self.video_display_scrollbar = self.video_display_scrollbar_run2

            if self.filter_frame_for_run2:
                self.filter_frame_for_run2.pack(side="left", fill="y", padx=10, pady=10)
            self.apply_video_filter1()
            print("일반 영상으로 바뀜")

        elif self.current_frame_index == 3: # 좋아요 영상 보기 페이지
            # 페이지네이션 버튼 및 라벨이 해당 페이지의 것으로 참조
            self.prev_page_button = self.prev_page_button_run3
            self.next_page_button = self.next_page_button_run3
            self.page_info_label = self.page_info_label_run3
            self.video_canvas = self.video_canvas_run3
            self.video_scrollable_frame = self.video_scrollable_frame_run3
            self.video_display_scrollbar = self.video_display_scrollbar_run3

            if self.filter_frame_for_run3:
                self.filter_frame_for_run3.pack(side="left", fill="y", padx=10, pady=10)
            self.apply_video_filter2()
            print("좋아요 영상으로 바뀜")
            
        # 페이지네이션 초기화
        self.current_video_page = 0


    def display_pagination_videos(self, video_info_list, parent_frame):
        # [1] 기존에 표시된 비디오 위젯들을 모두 지움
        for widget in parent_frame.winfo_children():
            widget.destroy()

        for video_info in video_info_list:
            # [2] 각 비디오를 위한 작은 프레임 생성
            video_frame = tk.Frame(parent_frame, bd=1, relief="solid", padx=5, pady=5, bg="white")
            video_frame.pack(fill="x", pady=2)

            # [3] 썸네일 로딩 및 표시
            thumbnail_url = video_info['thumbnails'].get("url")
            
            img_data = None
            tk_img = None
            if thumbnail_url:
                response = requests.get(thumbnail_url, timeout=5) # 썸네일 이미지 다운로드 (5초 타임아웃)
                img_data = response.content # 이미지 데이터를 바이트 형태로 가져옵니다.
                    
                # Pillow를 사용하여 이미지 데이터 열기, 크기 조정, Tkinter 호환 형식으로 변환
                img = Image.open(BytesIO(img_data))
                img = img.resize((120, 90), Image.Resampling.LANCZOS) # 썸네일 크기를 120x90으로 조정
                tk_img = ImageTk.PhotoImage(img)
            else:
                tk_img = self.placeholder_img # URL이 없을 경우 미리 만들어둔 이미지 사용

            thumbnail_label = tk.Label(video_frame, image=tk_img, bg="white")
            thumbnail_label.image = tk_img # Tkinter 이미지가 참조 유지
            thumbnail_label.pack(side="left", padx=5, pady=5) # 왼쪽으로 배치

            # [4] 비디오 정보(제목, 채널 이름) 표시
            info_frame = tk.Frame(video_frame, bg="white", width=500) # 너비 설정
            info_frame.pack_propagate(False) # 이 프레임이 자식 위젯의 크기에 따라 늘어나지 않도록 고정
            info_frame.pack(side="left", fill="y", expand=False, padx=(0, 5))

            title = video_info.get("title", "제목 없음") # 영상 제목
            # wraplength= 400: 텍스트가 이 너비를 넘으면 자동으로 줄바꿈
            tk.Label(info_frame, text=title, font=("Arial", 10, "bold"), wraplength=400, justify="left", bg="white").pack(anchor="w")

            channel_name = video_info.get("channel", "알 수 없는 채널") #채널 이름
            tk.Label(info_frame, text=channel_name, font=("Arial", 9), fg="gray", justify="left", bg="white").pack(anchor="w")
            
            if self.current_frame_index == 2: # 일반 영상 보기에 경우에만, 시청한 날짜가 존재함
                dateTime = dateTime_iso8601_to_dateTime(video_info.get("dateTime"))
                dateTime = dateTime.strftime('%Y-%m-%d %H:%M:%S')
                tk.Label(info_frame, text=dateTime, font=("Arial", 9), fg="gray", justify="left", bg="white").pack(anchor="w")

            video_url = video_info.get("video_url") # 유튜브 영상 URL
            tk.Button(info_frame, text="보기", command=lambda url=video_url: webbrowser.open(url), cursor="hand2").pack(anchor="e", pady=5)

        self.update_pagination_buttons()


    def update_pagination_buttons(self):
        # 이전/다음 버튼의 활성화 상태 업데이트
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page

        # 이전 버튼 활성화/비활성화
        if self.prev_page_button: 
            if self.current_video_page <= 0:
                self.prev_page_button.config(state="disabled")
            else:
                self.prev_page_button.config(state="normal")
        
        # 다음 버튼 활성화/비활성화
        if self.next_page_button: 
            if self.current_video_page >= total_pages - 1 or total_pages == 0:
                self.next_page_button.config(state="disabled")
            else:
                self.next_page_button.config(state="normal")


    def go_next_video_page(self):
        # 다음 페이지로 이동
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page
        if self.current_video_page < total_pages - 1:
            self.current_video_page += 1
            self.load_current_video_page()
            self.update_pagination_buttons()


    def go_prev_video_page(self):
        # 이전 페이지로 이동
        if self.current_video_page > 0:
            self.current_video_page -= 1
            self.load_current_video_page()
            self.update_pagination_buttons()


    def load_current_video_page(self):
        # 현재 페이지네이션 로딩
        # 영상 5개를 추출하여 display_videos로 전달
        start_index = self.current_video_page * self.videos_per_page
        end_index = start_index + self.videos_per_page
        
        # 전체 필터링된 영상 목록에서 현재 페이지에 해당하는 부분만 슬라이싱
        videos_to_show = self.total_filtered_videos[start_index:end_index]
        
        # 현재 페이지 보이기
        self.display_videos(videos_to_show, self.video_scrollable_frame)

        # 페이지 정보 레이블 업데이트
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page
        if total_pages == 0: # 영상이 없을 때 0/0으로 표시되도록
            self.page_info_label.config(text="페이지: 0/0")
        else:
            self.page_info_label.config(text=f"페이지: {self.current_video_page + 1}/{total_pages}")
 

    def apply_video_filter1(self):
        # 일반 영상 보기 페이지에서 필터 적용
        self.total_filtered_videos = list(self.video_info_list) 
        
        self.total_filtered_videos = sort_filter(self.total_filtered_videos, self.sort_combobox.get()) # 정렬 필터

        if self.subscribed_only_var.get():
            self.total_filtered_videos = sub_filter(self.total_filtered_videos) # 구독 여부 필터
        if self.selected_date_entry.get().strip():
            self.total_filtered_videos = date_filter(self.total_filtered_videos, self.selected_date_entry.get().strip()) # 날짜 필터
        if self.selected_channel_entry.get().strip():
            self.total_filtered_videos = channel_filter(self.total_filtered_videos, self.selected_channel_entry.get().strip()) # 채널 필터
        if self.selected_category_var.get() != "none":
            self.total_filtered_videos = category_filter(self.total_filtered_videos, self.selected_category_var.get()) # 카테고리 필터
        self.total_filtered_videos = platform_filter(self.total_filtered_videos, self.selected_platform_var.get()) # 플렛폼 필터
        
        # 페이지네이션 초기화
        self.current_video_page = 0

        # 현재 페이지네이션 로딩
        self.load_current_video_page()


    def apply_video_filter2(self):
        # 좋아요 영상 보기 페이지에서 필터 적용
        self.total_filtered_videos = list(self.liked_video_info_list)

        if self.selected_channel_var.get() != "<전체>":
            self.total_filtered_videos = channel_filter(self.total_filtered_videos, self.selected_channel_var.get()) # 채널 필터
        if self.selected_video_sort_var.get() != "<전체>":
            self.total_filtered_videos = video_sort_filter(self.total_filtered_videos, self.selected_video_sort_var.get()) # 쇼츠 필터

        # 페이지네이션 초기화
        self.current_video_page = 0

        # 현재 페이지네이션 로딩
        self.load_current_video_page()


    def create_video_display_widgets(self, parent_frame, page_type):
        # 비디오 목록을 담을 컨테이너
        video_display_container_frame = tk.Frame(parent_frame)
        video_display_container_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(video_display_container_frame, text="영상 기록 모아보기", font=("Arial", 16)).pack(pady=10)

        # 페이지 번호, 이전/다음 버튼 담는 프레임
        pagination_control_frame = tk.Frame(video_display_container_frame)
        pagination_control_frame.pack(pady=5)

        if page_type == 'run2':
            self.prev_page_button_run2 = tk.Button(pagination_control_frame, text="이전", command=self.go_prev_video_page, state="disabled")
            self.prev_page_button_run2.pack(side="left", padx=5)

            self.page_info_label_run2 = tk.Label(pagination_control_frame, text="페이지: 1/1")
            self.page_info_label_run2.pack(side="left", padx=10)

            self.next_page_button_run2 = tk.Button(pagination_control_frame, text="다음", command=self.go_next_video_page, state="disabled")
            self.next_page_button_run2.pack(side="left", padx=5)
        elif page_type == 'run3':
            self.prev_page_button_run3 = tk.Button(pagination_control_frame, text="이전", command=self.go_prev_video_page, state="disabled")
            self.prev_page_button_run3.pack(side="left", padx=5)

            self.page_info_label_run3 = tk.Label(pagination_control_frame, text="페이지: 1/1")
            self.page_info_label_run3.pack(side="left", padx=10)

            self.next_page_button_run3 = tk.Button(pagination_control_frame, text="다음", command=self.go_next_video_page, state="disabled")
            self.next_page_button_run3.pack(side="left", padx=5)
        
        # 영상 담는 프레임
        video_scrollable_frame = tk.Frame(video_display_container_frame, background="#f0f0f0")
        video_scrollable_frame.pack(side="left", fill="both", expand=True)

        # 각 페이지별 변수 설정
        if page_type == 'run2':
            self.video_display_container_frame_run2 = video_display_container_frame
            self.video_canvas_run2 = None
            self.video_display_scrollbar_run2 = None
            self.video_scrollable_frame_run2 = video_scrollable_frame
        elif page_type == 'run3':
            self.video_display_container_frame_run3 = video_display_container_frame
            self.video_canvas_run3 = None
            self.video_display_scrollbar_run3 = None
            self.video_scrollable_frame_run3 = video_scrollable_frame

        return video_display_container_frame



# 로그인 하는 함수
    def guest_user_login(self):
        self.youtube = guest_login()
        self.authority = "guest"
        self.show_page("start", 1)


    def teste_user_login(self):
        self.youtube = tester_login()
        self.authority = "tester"

        # 좋아요한 영상 정보
        self.liked_video_info_list = extract_video_info_from_liked_playlist(self.youtube)
        self.show_page("start", 1)



# 파일 불러오는 함수

    def save_file_loading(self):
        save_file_path = askopenfilename(
            title="저장한 파일 선택",
            filetypes=[("JSON files", "*.json")]
        )
        save_file = load_save_file(save_file_path)

        self.statistics = save_file["statistics"]
        self.sub_list = save_file["sub_list"]
        self.liked_video_info_list = save_file["liked_video_info_list"]
        self.video_info_list = save_file["video_info_list"]
        
        self.grapes = make_grapes(self.statistics)
        self.text_content = make_text(self.statistics)

        self.make_run_frame()


    def file_loading(self):
        # 1. 분석할 파일 경로 얻기
        # takeout.json 파일 경로
        takeout_file_path = askopenfilename(
            title="테이크아웃 파일 선택",
            filetypes=[("JSON files", "*.json")]
        )
        # 구독정보.csv 파일 경로
        sub_linfo_file_path = takeout_file_path[:-16] + "구독정보\\구독정보.csv"
    
        # 2. 분석할  파일 열기
        # takeout.json 파일 열기
        self.takeout = load_takeout_file(takeout_file_path)
        
        # 구독정보.csv 파일 열기
        self.sub_list = load_sub_file(sub_linfo_file_path)
        self.sub_list.append("<전체>")

        # 3. 쇼츠 영상 제외
        self.not_shorts_takeout = not_shorts_filter(self.takeout)

        # 4. 영상 id 추출(쇼츠 제외만)
        video_ids = extract_video_ids(self.not_shorts_takeout)

        # 5. 영상 정보 호출(쇼츠 제외만)
        self.video_info_list = call_video_info(self.youtube, video_ids, self.not_shorts_takeout, self.sub_list)

        # 6 통계 자료 얻기
        self.statistics = make_statistics(self.takeout, self.not_shorts_takeout, self.video_info_list, self.liked_video_info_list)
        self.text_content = make_text(self.statistics)

        # 7. 그래프 얻기
        self.grapes = make_grapes(self.statistics)

        # 디버깅 용
        print(f"불러온 영상: {len(self.video_info_list)}")
        print(f"총 추청 쇼츠 영상: {len(self.takeout) - len(self.video_info_list)}")

        self.make_run_frame()



# 파일 저장하는 함수 
    def save_file(self):
        save_file_path = asksaveasfilename(
            filetypes = [("JSON files", "*.json"), ("All files", "*.*")],
            title = "저장할 위치 선택"
            )
        save_all_data_to_json_file(self.statistics, self.sub_list, self.liked_video_info_list, self.video_info_list, save_file_path)
        print("저장됨")


    def save_grape_file(self):
        save_file_path = askdirectory(title = "저장할 위치 선택")
        save_file_path = save_file_path + "\\"
        save_all_grape(self.grapes, save_file_path)
        print("저장됨")




def YTVHApp_UI():
    app = YTVHApp()
    app.mainloop()
