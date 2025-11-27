from collections.abc import Callable
from tkinter import Canvas, Event, StringVar

from . import KVUtils
from .KVData import Marking

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .KVManager import KVManager

class KVInputHandler:
    def __init__(self, canvas: Canvas, kv_manager: KVManager, current_marking_getter: Callable[[], Marking]) -> None:
        self.resize_scheduled: bool = False
        canvas.bind("<Configure>", self.__get_on_resize(canvas))
        canvas.bind("<Button-1>", self.__get_on_left_click(current_marking_getter))
        canvas.bind("<Button-3>", self.__get_on_right_click(current_marking_getter))
        self.kv_manager = kv_manager
    
    def __get_on_resize(self, canvas: Canvas) -> Callable[[Event], None]:
        def update_sizes():
            self.resize_scheduled = False
            self.kv_manager.update_sizes(canvas.winfo_width(), canvas.winfo_height())
        def on_resize(event: Event) -> None:
            if not self.resize_scheduled:
                #schedule resize
                canvas.after(10, update_sizes)
                self.resize_scheduled = True
        return on_resize
    
    def __get_on_left_click(self, current_marking_getter: Callable[[], Marking]) -> Callable[[Event], None]:
        def on_left_click(event: Event) -> None:
            if (index := self.kv_manager.event_to_kv_index(event)) == -1:
                return
            current_indices = current_marking_getter().indices
            if len(current_indices) == 0:
                current_indices.append(index)
            elif (different_bit := KVUtils.get_different_bit(index, current_indices)) is not None:    
                KVUtils.expand_block(current_indices, different_bit)
            else:
                return
            self.kv_manager.update_selected_marking()
        return on_left_click
    
    def __get_on_right_click(self, current_marking_getter: Callable[[], Marking]) -> Callable[[Event], None]:
        def on_right_click(event: Event) -> None:
            current_marking = current_marking_getter()
            current_indices = current_marking.indices
            if len(current_indices) == 0:
                return
            if len(current_indices) == 1:
                self.kv_manager.remove_selected_marking()
                return
            if (index := self.kv_manager.event_to_kv_index(event)) in current_indices:
                KVUtils.shrink_block(current_indices, index)
                self.kv_manager.update_selected_marking()
        return on_right_click
    
    def link_vals(self, vals: StringVar) -> None:
        def vals_changed() -> None:
            self.kv_manager.update_vals(vals.get())
        vals.trace_add('write', lambda name, index, mode: vals_changed())
    
    def link_vars(self, vars: StringVar) -> None:
        def vars_changed() -> None:
            self.kv_manager.update_vars(vars.get().split(","))
        vars.trace_add('write', lambda name, index, mode: vars_changed())
    
    def link_marking_color(self, marking_color: StringVar) -> None:
        def marking_color_changed() -> None:
            self.kv_manager.color_changed(marking_color.get())
        marking_color.trace_add('write', lambda name, inddex, mode: marking_color_changed())