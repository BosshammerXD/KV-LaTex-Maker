from collections.abc import Callable
from tkinter import Menu, Misc, OptionMenu, StringVar

from Globals import DYNAMIC
from IterTools import CyclicCache
from KV_Diagramm.Dataclasses.Marking import Marking


class KVColorsMenu(OptionMenu):
    def __init__(self, master: Misc) -> None:
        self.__colors: CyclicCache[str] = CyclicCache(iter(DYNAMIC.Colors))
        self.__current_color: StringVar = StringVar(value=self.__colors.get_item())
        super().__init__(master, self.__current_color, *DYNAMIC.Colors)
        self.__callback: Callable[[str], None] = lambda _: None
        self.__current_color.trace_add('write', self.__on_color_change)
        self.__got_next_color: bool = False
    
    def get_color(self) -> str:
        return self.__current_color.get()

    def set_color_from_marking(self, marking: Marking) -> None:
        self.__current_color.set(marking.latex_color)
    
    def next_color(self) -> str:
        self.__got_next_color = True
        new_color = self.__colors.get_item()
        self.__current_color.set(new_color)
        return new_color
    
    def release_marking_color(self, marking: Marking) -> None:
        self.__colors.release_item(marking.latex_color)

    def update_options(self, generate_new_color: bool):
        menu: Menu = self["menu"]
        menu.delete(0, "end")
        for opt in DYNAMIC.Colors.keys():
            menu.add_command(label=opt, command=lambda: self.__current_color.set(opt))
        if generate_new_color:
            self.__current_color.set(next(iter(DYNAMIC.Colors)))
        self.__colors.change_generator(iter(DYNAMIC.Colors), self.__current_color.get())
    
    def trace_color(self, callback: Callable[[str], None]) -> None:
        self.__callback = callback
    
    def __on_color_change(self, name: str, index: str, mode: str) -> None:
        if not self.__got_next_color:
            self.__callback(self.__current_color.get())
        else:
            self.__got_next_color = False
