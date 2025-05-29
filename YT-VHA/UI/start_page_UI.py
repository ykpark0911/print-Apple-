import tkinter as tk
from tkinter.filedialog import askopenfilename
import webbrowser
from yt_api.get_yt_ob import oauth_login, guest_login

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


    
    def select_takeout_file(self):
        file_path = askopenfilename(
            title="테이크아웃 파일 선택",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self.takeout_path = file_path
            print("파일 경로:", self.takeout_path)  # ✅ 경로가 콘솔에 출력됨
        
        self.next_button.config(state="normal")

    def create_page1(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="YTVH (YouTube View History Analyzer)", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="게스트", command=self.next_page, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="테스트 사용자", command=self.next_page, width=20, height=2).pack(pady=10)
        return frame

    def create_page2(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="비교 모드 선택", font=("Arial", 16)).pack(pady=20)
        tk.Button(frame, text="혼자서 비교", command=self.next_page, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="2명 비교", command=self.next_page, width=20, height=2).pack(pady=10)
        return frame

    def create_page3(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="테이크아웃 파일 불러오기", font=("Arial", 16)).pack(pady=20)
        link = tk.Label(frame, text="테이크아웃 링크 열기", fg="blue", cursor="hand2", font=("Arial", 12, "underline"))
        link.pack(pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://takeout.google.com/"))

        tk.Button(frame, text="파일 올리기", width=20, height=2, command= self.select_takeout_file).pack(pady=5)
        self.next_button = tk.Button(frame, text="넘어가기", state="disabled", command=self.next_page, width=20, height=2) #여기다가 pack 붙이면 변수에 None이 저장되는꼴
        self.next_button.pack(pady=20)
        return frame

    def create_final_page(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="✅ 프로그램 실행창!", font=("Arial", 20), fg="green").pack(pady=100)
        return frame

if __name__ == "__main__":
    app = YTVHApp()
    app.mainloop()
