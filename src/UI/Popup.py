from Globals.STATIC import ROOT
from collections.abc import Callable
from tkinter import Toplevel, Label, Frame, Button


class Popup:
    def __init__(self, title: str, message: str):
        self.__title = title
        self.__message = message
        self.__buttons: list[tuple[str, Callable[[], None]]] = []
        
    
    def show(self) -> Toplevel:
        self.win = Toplevel()
        self.win.deiconify()
        self.win.wm_title(self.__title)
        self.win.rowconfigure(0, weight=1)
        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)
        Label(self.win, text=self.__message).grid(row=0, column=0)

        self.__button_frame = Frame(self.win)
        self.__button_frame.grid(row=1, column=0, sticky="ew")
        self.__column_counter = 0

        for text, command in self.__buttons:
            self.__button_frame.columnconfigure(self.__column_counter, weight=1)
            button = Button(self.__button_frame, text=text, command=self.__destroy_wrapper(command))
            button.grid(column=self.__column_counter, row=0, sticky="ew")
            self.__column_counter += 1
        
        return self.win

            
    
    def add_button(self, text: str, command: Callable[[], None]) -> None:
        self.__buttons.append((text, self.__destroy_wrapper(command)))
    
    def __destroy_wrapper(self, func: Callable[[], None]) -> Callable[[], None]:
        def wrapper() -> None:
            self.win.destroy()
            func()
        
        return wrapper

def wait_for_pop_up(win: Toplevel, hide: bool = False):
    if hide: ROOT.withdraw()
    ROOT.wait_window(win)
    if hide: ROOT.deiconify()
    