import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from tkinter.filedialog import askopenfilename, asksaveasfilename
import webbrowser
from yt_api.get_yt_ob import tester_login, guest_login
from open_file.extract_video_ids import extract_video_ids_from_watch_history # 영상 id 뽑아내는 함수
from open_file.get_sub_list import get_sub_list
from open_file.json_loader import load_json # takeout 파일 여는 함수
from yt_api.get_video_info import get_video_info # 영상 정보 호출하는 함수
from yt_api.get_liked_video_info import extract_video_info_from_liked_playlist
from filter import * # 쇼츠 영상 제외 시키는 필터 함수 
from video_statistics import make_statistics
from save_file.save_statistics import save_statistics_to_file
from grape import make_grapes, empty_grape
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class YTVHApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YTVH - YouTube View History Analyzer")
        self.geometry("800x600")

        # 각종 변수 초기화
        # 영상 관련 리스트 초기화
        self.video_info_list = []
        self.sub_list= []
        self.liked_video_info_list = []
        
        # 필터링 관련 변수 초기화
        self.subscribed_only_var = tk.BooleanVar(value=False)
        self.selected_date_entry = None
        self.selected_channel_entry = None
        self.selected_category_var = tk.StringVar(value="none")
        self.selected_platform_var = tk.StringVar(value="YouTube")
        self.selected_channel_var = tk.StringVar(value="<전체>") # 좋아요 영상 필터용

        # **모든 run 페이지에서 공통으로 사용될 비디오 표시 및 페이지네이션 위젯 초기화**
        # 이 위젯들은 나중에 create_run_page2, create_run_page3에 인자로 전달하거나,
        # 각 페이지 프레임에 직접 pack하여 사용합니다.
        self.video_display_container_frame_run2 = None 
        self.video_canvas_run2 = None                 
        self.video_display_scrollbar_run2 = None
        self.video_scrollable_frame_run2 = None       

        self.video_display_container_frame_run3 = None 
        self.video_canvas_run3 = None                 
        self.video_display_scrollbar_run3 = None
        self.video_scrollable_frame_run3 = None     
        
        # 필터 프레임들을 미리 초기화 (나중에 create_run_page2/3에서 실제 위젯 생성)
        self.filter_frame_for_run2 = None 
        self.filter_frame_for_run3 = None
        self.subscribed_channels_radio_frame = None # 구독 채널 라디오 버튼용 프레임

        # 영상 보여주기 페이지 초기화
        self.current_video_page = 0    # 현재 비디오 페이지 (0부터 시작)
        self.videos_per_page = 5       # 한 페이지에 보여줄 영상 개수
        self.total_filtered_videos = [] # 현재 필터링된 전체 영상 목록 (페이지네이션 대상)
        self.placeholder_img = ImageTk.PhotoImage(Image.new("RGB", (120, 90), color = 'gray'))

        # 프레임 구성
        start_page_frames = {
            0 : self.create_start_frame0(),
            1 : self.create_start_frame1(),
        }

        # 페이지 구성
        self.pages = {"start" : start_page_frames}

        # 첫 페이지 보여주기
        self.current_frame_index = 0
        self.current_page = "start"
        self.show_page("start", 0)


    def create_video_display_widgets(self, parent_frame, page_type):
        """
        비디오 목록 표시 및 페이지네이션을 위한 공통 위젯들을 생성합니다.
        이 위젯들은 모든 비디오 보기 페이지에서 재사용됩니다.
        """
        # 비디오 목록을 담을 컨테이너
        video_display_container_frame = tk.Frame(parent_frame)
        video_display_container_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(video_display_container_frame, text="영상 기록 모아보기", font=("Arial", 16)).pack(pady=10)

        # 페이지네이션 컨트롤 프레임 (페이지 번호, 이전/다음 버튼)
        pagination_control_frame = tk.Frame(video_display_container_frame)
        pagination_control_frame.pack(pady=5)

        self.prev_page_button = tk.Button(pagination_control_frame, text="이전", command=self.go_prev_video_page, state="disabled")
        self.prev_page_button.pack(side="left", padx=5)

        self.page_info_label = tk.Label(pagination_control_frame, text="페이지: 1/1")
        self.page_info_label.pack(side="left", padx=10)

        self.next_page_button = tk.Button(pagination_control_frame, text="다음", command=self.go_next_video_page, state="disabled")
        self.next_page_button.pack(side="left", padx=5)


        video_scrollable_frame = tk.Frame(video_display_container_frame, background="#f0f0f0")
        video_scrollable_frame.pack(side="left", fill="both", expand=True) # 이제 이 프레임이 직접 채워집니다.
        
        # 수정: 각 페이지별 멤버 변수에 할당하여 충돌 방지
        if page_type == 'run2':
            self.video_display_container_frame_run2 = video_display_container_frame
            self.video_canvas_run2 = None  # Canvas 제거
            self.video_display_scrollbar_run2 = None # Scrollbar 제거
            self.video_scrollable_frame_run2 = video_scrollable_frame
        elif page_type == 'run3':
            self.video_display_container_frame_run3 = video_display_container_frame
            self.video_canvas_run3 = None  # Canvas 제거
            self.video_display_scrollbar_run3 = None # Scrollbar 제거
            self.video_scrollable_frame_run3 = video_scrollable_frame
        
        return video_display_container_frame


    def show_page(self, page, index):
        # 모든 프레임을 숨깁니다.
        for page_group in self.pages.values():
            for frame_item in page_group.values():
                frame_item.pack_forget()

        # 현재 페이지의 프레임을 보여줍니다.
        self.pages[page][index].pack(expand=True, fill="both")

        self.current_frame_index = index
        self.current_page = page

        # 'run' 페이지의 특정 인덱스에서 비디오 필터링 및 로드
        if page == "run" and index in (2, 3):
            # 공통 비디오 표시 컨테이너를 현재 페이지 프레임에 추가/제거
            # (이는 create_common_video_display_widgets에서 이미 부모 프레임에 pack되므로, 
            #  여기서는 딱히 조작할 필요가 없습니다.

            if index == 2: # 일반 영상 보기 페이지
                self.total_filtered_videos = self.video_info_list
                if self.filter_frame_for_run2: self.filter_frame_for_run2.pack(side="left", fill="y", padx=10, pady=10)
                self.video_canvas = self.video_canvas_run2
                self.video_scrollable_frame = self.video_scrollable_frame_run2
                self.video_display_scrollbar = self.video_display_scrollbar_run2
                self.apply_video_filter()
                print("일반 영상으로 바뀜")
            elif index == 3: # 좋아요 영상 보기 페이지
                self.total_filtered_videos = self.liked_video_info_list
                if self.filter_frame_for_run3: self.filter_frame_for_run3.pack(side="left", fill="y", padx=10, pady=10)
                self.video_canvas = self.video_canvas_run3
                self.video_scrollable_frame = self.video_scrollable_frame_run3
                self.video_display_scrollbar = self.video_display_scrollbar_run3
                self.apply_video_filter2()
                print("좋아요 영상으로 바뀜")
            
            # 페이지네이션 초기화 및 첫 페이지 로드
            self.current_video_page = 0
            self.load_current_video_page() 
    
    # name은 "shorts_distribution" 등 ...
    def show_grape(self, grape_sort, parent_frame, include_short_or_not_key=False):
        if include_short_or_not_key:
            grape = self.grapes[grape_sort][include_short_or_not_key]
        else:
            grape = self.grapes[grape_sort]
        
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(grape, master=parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def display_videos(self, video_info_list, parent_frame):
        # **[1] 기존에 표시된 비디오 위젯들을 모두 지웁니다.**
        # 이 부분이 중요합니다. 새 목록을 표시할 때 이전 목록이 남아있지 않도록 합니다.
        for widget in parent_frame.winfo_children():
            widget.destroy()

        for video_info in video_info_list:
            # **[2] 각 비디오를 위한 작은 프레임 생성**
            video_frame = tk.Frame(parent_frame, bd=1, relief="solid", padx=5, pady=5, bg="white") # 흰색 배경, 테두리
            video_frame.pack(fill="x", pady=2) # 가로로 꽉 채우고 상하 여백 주기

            # **[3] 썸네일 로딩 및 표시**
            thumbnail_url = video_info['thumbnails'].get("url")
            
            img_data = None
            tk_img = None
            if thumbnail_url:
                response = requests.get(thumbnail_url, timeout=5) # 썸네일 이미지 다운로드 (5초 타임아웃)
                response.raise_for_status() # HTTP 오류 (4xx, 5xx)가 발생하면 예외 발생
                img_data = response.content # 이미지 데이터를 바이트 형태로 가져옵니다.
                    
                # Pillow를 사용하여 이미지 데이터 열기, 크기 조정, Tkinter 호환 형식으로 변환
                img = Image.open(BytesIO(img_data))
                img = img.resize((120, 90), Image.Resampling.LANCZOS) # 썸네일 크기를 120x90으로 조정
                tk_img = ImageTk.PhotoImage(img)
            else:
                tk_img = self.placeholder_img # URL이 없을 경우에도 플레이스홀더 사용

            thumbnail_label = tk.Label(video_frame, image=tk_img, bg="white")
            thumbnail_label.image = tk_img # **매우 중요!** Tkinter 이미지가 가비지 컬렉트되지 않도록 참조 유지
            thumbnail_label.pack(side="left", padx=5, pady=5) # 왼쪽으로 배치

            # **[4] 비디오 정보 (제목, 채널 이름) 표시**
            info_frame = tk.Frame(video_frame, bg="white") # 제목과 채널명을 담을 프레임
            info_frame.pack(side="left", fill="x", expand=True) # 썸네일 오른쪽에 붙고, 남은 공간을 가로로 채움

            title = video_info.get("title", "제목 없음") # 'title' 키가 없으면 "제목 없음"으로 표시
            # `wraplength`는 텍스트가 이 너비를 넘으면 자동으로 줄바꿈됩니다.
            tk.Label(info_frame, text=title, font=("Arial", 10, "bold"), wraplength=400, justify="left", bg="white").pack(anchor="w")

            channel_name = video_info.get("channel", "알 수 없는 채널") # 'channel_name' 키가 없으면 "알 수 없는 채널"로 표시
            tk.Label(info_frame, text=channel_name, font=("Arial", 9), fg="gray", justify="left", bg="white").pack(anchor="w")

            # **[5] 유튜브 링크 열기 버튼 (선택 사항)**
            video_url = video_info.get("video_url") # 유튜브 영상 URL 형식
            tk.Button(info_frame, text="보기", command=lambda url=video_url: webbrowser.open(url), cursor="hand2").pack(anchor="e", pady=5)

        self.update_pagination_buttons()
        

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


    def apply_video_filter(self):
        # ... (기존 apply_video_filter 함수 코드) ...
        # (생략: 기존 apply_video_filter 함수 내용은 그대로 두시면 됩니다.)
        self.total_filtered_videos = self.video_info_list

        if self.subscribed_only_var.get():
            self.total_filtered_videos = sub_filter(self.total_filtered_videos)
        if self.selected_date_entry.get().strip():
            print(f"디버그: 날짜 필터 - 입력된 날짜: '{self.selected_date_entry.get().strip()}'")
            self.total_filtered_videos = date_filter(self.total_filtered_videos, self.selected_date_entry.get().strip())
        if self.selected_channel_entry.get().strip():
            print(f"디버그: 채널 필터 - 입력된 채널: '{self.selected_channel_entry.get().strip()}'")
            self.total_filtered_videos = channel_filter(self.total_filtered_videos, self.selected_channel_entry.get().strip())
        if self.selected_category_var.get() != "none":
            self.total_filtered_videos = category_filter(self.total_filtered_videos, self.selected_category_var.get())
        self.total_filtered_videos = platform_filter(self.total_filtered_videos, self.selected_platform_var.get())
        
        self.current_video_page = 0
        self.load_current_video_page()

    def apply_video_filter2(self):
        self.total_filtered_videos = self.liked_video_info_list

        if self.selected_channel_var.get() != "<전체>":
            self.total_filtered_videos = channel_filter(self.total_filtered_videos, self.selected_channel_var.get())

        self.current_video_page = 0
        self.load_current_video_page()

    def load_current_video_page(self):
        """현재 페이지에 해당하는 영상 5개를 추출하여 display_videos로 전달합니다."""
        start_index = self.current_video_page * self.videos_per_page
        end_index = start_index + self.videos_per_page
        
        # 전체 필터링된 영상 목록에서 현재 페이지에 해당하는 부분만 잘라냅니다.
        videos_to_show = self.total_filtered_videos[start_index:end_index]
        
        self.display_videos(videos_to_show, self.video_scrollable_frame)
        # 페이지 정보 레이블 업데이트
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page
        if total_pages == 0: # 영상이 없을 때 0/0으로 표시되도록
            self.page_info_label.config(text="페이지: 0/0")
        else:
            self.page_info_label.config(text=f"페이지: {self.current_video_page + 1}/{total_pages}")
    

    def go_next_video_page(self):
        """다음 페이지로 이동합니다."""
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page
        if self.current_video_page < total_pages - 1:
            self.current_video_page += 1
            self.load_current_video_page()
            self.update_pagination_buttons()

    def go_prev_video_page(self):
        """이전 페이지로 이동합니다."""
        if self.current_video_page > 0:
            self.current_video_page -= 1
            self.load_current_video_page()
            self.update_pagination_buttons()

    def update_pagination_buttons(self):
        """이전/다음 버튼의 활성화 상태를 업데이트합니다."""
        total_pages = (len(self.total_filtered_videos) + self.videos_per_page - 1) // self.videos_per_page

        # 이전 버튼 활성화/비활성화
        if self.current_video_page <= 0:
            self.prev_page_button.config(state="disabled")
        else:
            self.prev_page_button.config(state="normal")
        
        # 다음 버튼 활성화/비활성화
        if self.current_video_page >= total_pages - 1 or total_pages == 0:
            self.next_page_button.config(state="disabled")
        else:
            self.next_page_button.config(state="normal")
        
        if total_pages == 0:
            self.page_info_label.config(text="페이지: 0/0")
        else:
            self.page_info_label.config(text=f"페이지: {self.current_video_page + 1}/{total_pages}")


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
    
    def file_loading(self):
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
        self.sub_list = get_sub_list(sub_linfo_file_path)

        # 영상 id 추출(쇼츠 제외만)
        video_ids = extract_video_ids_from_watch_history(self.not_shorts_takeout)
        print("아이디 추출 완료")

        # 영상 정보 호출(쇼츠 제외만)
        self.video_info_list = get_video_info(self.youtube, video_ids, self.not_shorts_takeout, self.sub_list)
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

        run_page_frames = {
            0 : self.create_run_page0(),
            1 : self.create_run_page1(),
            2 : self.create_run_page2(),
            3 : self.create_run_page3()
        }
        self.pages["run"] = run_page_frames

           
    def create_start_frame0(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="YTVH (YouTube View History Analyzer)", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="게스트 사용자", command=self.guest_user_login, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="테스트 사용자", command=self.teste_user_login, width=20, height=2).pack(pady=10)
        
        return frame

    def create_start_frame1(self):
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
        tk.Button(frame, text="2. 일반 영상 보기", width=20, height=2,
                  command=lambda: self.show_page(self.current_page, 2)).pack(pady=10)
        tk.Button(frame, text="3. 좋아요 영상 보기", width=20, height=2,
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
        # **[1] 좌측 필터 프레임과 우측 영상 표시 컨테이너 프레임을 나눕니다.**
        # `side="left"`와 `side="right"`를 사용하여 좌우로 배치합니다.
        filter_frame = tk.Frame(frame, bd=2, relief="groove", width=200) # 필터링 영역 (테두리 및 고정 너비)
        filter_frame.pack(side="left", fill="y", padx=10, pady=10) # y축으로 채우기
        filter_frame.pack_propagate(False) # 이 프레임의 크기가 자식 위젯에 의해 변경되지 않도록 고정

        video_display_container_frame = tk.Frame(frame) # 비디오 목록을 담을 컨테이너
        video_display_container_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10) # 남은 공간을 모두 채우고 확장 가능하게

        # --- 왼쪽 컬럼: 필터링 옵션 ---
        tk.Label(filter_frame, text="필터링 옵션", font=("Arial", 12, "bold")).pack(pady=10)

        # 1. 구독한 채널 필터 (체크박스)
        tk.Checkbutton(filter_frame, text="구독한 채널만 보기", variable=self.subscribed_only_var).pack(anchor="w", padx=5, pady=2)
        
        # 2. 선택한 날짜 필터 (입력 필드)
        tk.Label(filter_frame, text="날짜 선택 (YYYY-MM-DD):").pack(anchor="w", padx=5, pady=2)
        self.selected_date_entry = tk.Entry(filter_frame)
        self.selected_date_entry.pack(fill="x", padx=5, pady=2)

        # 3. 선택한 채널 필터 (입력 필드)
        tk.Label(filter_frame, text="채널 이름 입력:").pack(anchor="w", padx=5, pady=2)
        self.selected_channel_entry = tk.Entry(filter_frame)
        self.selected_channel_entry.pack(fill="x", padx=5, pady=2)


        # 4. 선택한 카테고리 필터 (라디오 버튼)
        tk.Label(filter_frame, text="카테고리 선택:").pack(anchor="w", padx=5, pady=2)
        self.categories = {
            "none": "선택 안 함",
            "1": "Film & Animation",
            "2": "Autos & Vehicles",
            "10": "Music",
            "15": "Pets & Animals",
            "17": "Sports",
            "20": "Gaming",
            "22": "People & Blogs",
            "23": "Comedy",
            "24": "Entertainment",
            "25": "News & Politics",
            "26": "Howto & Style",
            "27": "Education",
            "28": "Science & Technology",
            "29": "Nonprofits & Activism"
        }
        for category_id, category_name in self.categories.items():
            tk.Radiobutton(filter_frame, text=category_name, variable=self.selected_category_var, value=category_id).pack(anchor="w", padx=5, pady=1)

        # 5. 플랫폼 필터 (라디오 버튼)
        tk.Label(filter_frame, text="플랫폼 선택:").pack(anchor="w", padx=5, pady=10)

        tk.Radiobutton(filter_frame, text="YouTube", variable=self.selected_platform_var, value="YouTube").pack(anchor="w", padx=5, pady=2)

        tk.Radiobutton(filter_frame, text="YouTube Music", variable=self.selected_platform_var, value="YouTube Music").pack(anchor="w", padx=5, pady=2)
        
        # --- 완료 버튼 (모든 필터 설정을 적용) ---
        tk.Button(filter_frame, text="필터 적용", command=self.apply_video_filter).pack(anchor="w", padx=5, pady=15, fill="x")
        
        # --- 오른쪽 컬럼: 비디오 표시 영역 및 페이지네이션 컨트롤 ---
        self.video_display_container_frame = self.create_video_display_widgets(frame, 'run2')

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

        tk.Label(filter_frame, text="채널 선택:").pack(anchor="w", padx=5, pady=2)
        self.sub_list.append("<전체>")
        for channel_name in self.sub_list:
            tk.Radiobutton(filter_frame, text=channel_name, variable=self.selected_channel_var , value=channel_name).pack(anchor="w", padx=5, pady=1)

        # --- 완료 버튼 (모든 필터 설정을 적용) ---
        tk.Button(filter_frame, text="필터 적용", command=self.apply_video_filter2).pack(anchor="w", padx=5, pady=15, fill="x")

       # 우측 비디오 표시 컨테이너 (공통 함수로 생성)
        self.video_display_container_frame = self.create_video_display_widgets(frame, 'run3')

        # 뒤로가기 버튼은 맨 아래에 배치
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack(side="bottom", pady=10)

        return frame


def YTVHApp_UI():
    app = YTVHApp()
    app.mainloop()
