from tkinter import Frame, Misc, Widget, Event
from typing import Callable

class ScrollingFrame(Frame):
    def __init__(self, master: Misc):
        super().__init__(master)
        self.bind("<MouseWheel>", self.__scroll_event) #Widows/Mac
        self.bind("<Button-4>", self.__scroll_event) #Linux
        self.bind("<Button-5>", self.__scroll_event) #Linux

        self.__scroll_progress: float = 0
        self.__height = 0
        self.__height_dirty: bool = False
        self.__items: list[Widget] = []

    def __edit_tags(self, child: Widget, editor: Callable[[list[str]], None]):
        tags: list[str] = list(child.bindtags())
        editor(tags)
        child.bindtags(tags)
        for c in child.winfo_children():
            self.__edit_tags(c, editor)

    def add_child(self, child: Widget):
        self.__items.append(child)
        child.place_forget()
        self.__edit_tags(child, lambda l: l.insert(1, str(self)))
        self.__set_height_dirty_and_render()
    
    def remove_child(self, child: Widget):
        self.__items.remove(child)
        child.place_forget()
        self.__edit_tags(child, lambda l: l.remove(str(self)))
        self.__set_height_dirty_and_render()

    def __set_height_dirty_and_render(self):
        self.__height_dirty
        self.after_idle(self.render)

    def __update_height(self):
        for widget in self.__items:
            widget.place()
        self.update_idletasks()
        self.__height = sum(child.winfo_height() for child in self.__items)

    def __get_height(self):
        if self.__height_dirty:
            self.__height_dirty = False
            self.__update_height()
        return self.__height

    def render(self):
        self.__update_height()
        acc: float = -self.__scroll_progress
        for widget in self.__items:
            widget.place(
                x = 0,
                y = acc,
                width=self.winfo_width()
            )
            acc += widget.winfo_height()

    def __scroll_event(self, event: Event):
        delta = -event.delta * 0.1
        height = self.__get_height() - self.winfo_height()
        if (self.__scroll_progress + delta < 0):
            delta = -self.__scroll_progress
            if self.__scroll_progress == 0:
                return
            self.__scroll_progress = 0
        elif (self.__scroll_progress + delta > height):
            delta = max(0, height) - self.__scroll_progress
            if self.__scroll_progress == height:
                return
            self.__scroll_progress = max(0, height)
        else:
            self.__scroll_progress += delta
        self.render()

