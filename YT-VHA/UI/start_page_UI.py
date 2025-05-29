import tkinter as tk

class PageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("페이지 스택 구조 예제")
        self.geometry("400x200")

        self.current_page = 0  # 현재 페이지 인덱스
        self.pages = []        # 페이지(Frame) 리스트

        # 페이지 프레임들 생성
        for i in range(1, 4):  # 1~3페이지
            page = self.create_page(f"{i} 페이지입니다")
            self.pages.append(page)

        # 처음 페이지 보여주기
        self.show_page(0)

        # 이전/다음 버튼
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="← 이전", command=self.prev_page).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="다음 →", command=self.next_page).grid(row=0, column=1, padx=10)

    def create_page(self, text):
        frame = tk.Frame(self)
        label = tk.Label(frame, text=text, font=("Arial", 20))
        label.pack(expand=True)
        frame.place(x=0, y=0, relwidth=1, relheight=1)
        return frame

    def show_page(self, index):
        self.current_page = index
        self.pages[index].tkraise()

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

if __name__ == "__main__":
    app = PageApp()
    app.mainloop()
