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
        self.video_info_list = []

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

        # 영상 보여주기 페이지 초기
        self.current_video_page = 0    # 현재 비디오 페이지 (0부터 시작)
        self.videos_per_page = 5       # 한 페이지에 보여줄 영상 개수
        self.total_filtered_videos = [] # 현재 필터링된 전체 영상 목록 (페이지네이션 대상)
        self.placeholder_img = ImageTk.PhotoImage(Image.new("RGB", (120, 90), color = 'gray'))

    def show_page(self, page, index):
        for page_dict in self.pages.values():
            for frame in page_dict.values():
                frame.pack_forget()

        self.pages[page][index].pack(expand=True, fill="both")

        self.current_frame_index = index
        self.current_page = page

        if page == "run" and index == 2:
            self.apply_video_filter()
            # 페이지네이션 초기화 및 첫 페이지 로드
            self.current_video_page = 0 # 페이지 이동 시 현재 페이지를 0으로 초기화
            self.apply_video_filter()   # 필터링 및 첫 페이지 비디오 로드
    
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
            
        # **[6] 모든 위젯 배치 후 스크롤 영역 업데이트**
        # 이 부분이 없으면 스크롤바가 제대로 작동하지 않을 수 있습니다.
        self.video_canvas.update_idletasks() # Tkinter가 모든 위젯의 크기와 위치를 계산하도록 강제합니다.
        self.video_canvas.configure(scrollregion=self.video_canvas.bbox("all")) # Canvas의 스크롤 영역을 모든 내용물에 맞춰 다시 설정합니다.

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
        selected_filter = self.filter_var.get()
        self.total_filtered_videos = list(self.video_info_list) 

        # 필터 없음 ('none')은 정렬하지 않고 원본 순서대로 표시합니다.
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
        
        # 페이지 정보 레이블 업데이트 (load_current_video_page에서도 업데이트되지만, 안전을 위해 여기에 다시 호출)
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

        self.filter_var = tk.StringVar(value="none") # 선택된 필터 값을 저장할 변수 (초기값은 '필터 없음')
        
        tk.Radiobutton(filter_frame, text="필터 없음", variable=self.filter_var, value="none",
                       command=self.apply_video_filter).pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(filter_frame, text="시청 시간 순 (오름차순)", variable=self.filter_var, value="watch_time_asc",
                       command=self.apply_video_filter).pack(anchor="w", padx=5, pady=2)
        tk.Radiobutton(filter_frame, text="시청 시간 순 (내림차순)", variable=self.filter_var, value="watch_time_desc",
                       command=self.apply_video_filter).pack(anchor="w", padx=5, pady=2)

        # 필요에 따라 더 많은 필터 옵션을 추가하세요.

        # --- 오른쪽 컬럼: 비디오 표시 영역 및 페이지네이션 컨트롤 ---
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

        # **[2] 스크롤 가능한 영역을 만들기 위한 tk.Canvas 및 tk.Scrollbar**
        # Canvas는 그림을 그릴 수 있는 영역이자, 스크롤 가능한 "창" 역할을 합니다.
        self.video_canvas = tk.Canvas(video_display_container_frame, borderwidth=0, background="#f0f0f0") # 테두리 없음, 밝은 회색 배경
        
        # Scrollbar는 Canvas와 연동되어 스크롤 기능을 제공합니다.
        self.video_display_scrollbar = tk.Scrollbar(video_display_container_frame, orient="vertical", command=self.video_canvas.yview)
        
        # **[3] 실제 비디오 항목들이 배치될 프레임 (Canvas 안에 생성)**
        # 이 프레임은 Canvas의 "창" 역할을 하는 곳에 실제 내용을 담는 곳입니다.
        self.video_scrollable_frame = tk.Frame(self.video_canvas, background="#f0f0f0") # Canvas와 동일한 배경색

        # **[4] 스크롤 가능 프레임의 크기가 변경될 때 Canvas의 스크롤 영역을 업데이트합니다.**
        # `bbox("all")`은 `self.video_scrollable_frame` 안에 있는 모든 내용물의 경계 상자를 계산합니다.
        # 이 경계 상자가 Canvas의 `scrollregion`이 되어야 스크롤바가 내용물 길이에 맞춰 움직입니다.
        self.video_scrollable_frame.bind(
            "<Configure>", # 프레임의 크기가 변경될 때 이 이벤트를 발생시킵니다.
            lambda e: self.video_canvas.configure(
                scrollregion=self.video_canvas.bbox("all") # 전체 내용물의 크기에 맞춰 스크롤 영역 설정
            )
        )

        # **[5] 스크롤 가능 프레임을 Canvas 안에 "윈도우"로 추가합니다.**
        # (0, 0)은 Canvas의 왼쪽 위 모서리입니다. `anchor="nw"`는 프레임의 왼쪽 위를 Canvas의 (0,0)에 맞춥니다.
        self.video_canvas.create_window((0, 0), window=self.video_scrollable_frame, anchor="nw")
        
        # **[6] Canvas에 스크롤바를 연결합니다.**
        # `yscrollcommand`는 Canvas의 Y축 스크롤을 Scrollbar의 `set` 메서드와 연결합니다.
        self.video_canvas.configure(yscrollcommand=self.video_display_scrollbar.set)

        # **[7] Canvas와 Scrollbar를 화면에 배치합니다.**
        self.video_canvas.pack(side="left", fill="both", expand=True) # Canvas가 왼쪽을 채우고 확장 가능하게
        self.video_display_scrollbar.pack(side="right", fill="y") # Scrollbar가 Canvas 오른쪽에 붙어 세로로 채우게

        # 뒤로가기 버튼은 맨 아래에 배치
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack(side="bottom", pady=10)

        return frame
    
    def create_run_page3(self):
        frame = tk.Frame(self)
        tk.Label(frame, text=f"좋아요한 영상 기록 모아보기", font=("Arial", 20)).pack(pady=100)
        tk.Button(frame, text="🔙 뒤로가기", command=lambda: self.show_page(self.current_page, 0)).pack()

        return frame


def YTVHApp_UI():
    app = YTVHApp()
    app.mainloop()
