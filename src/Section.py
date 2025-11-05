from tkinter import Frame, Label, Misc


class Section:
    def __init__(self, master: Misc | None, title: str):
        self.frame: Frame = Frame(master, border=5, relief="groove")
        self.frame.pack(fill="x", pady=0)
        Label(self.frame, text=title, font="large_font").pack(fill="x", pady=5)