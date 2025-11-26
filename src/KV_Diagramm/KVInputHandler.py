from collections.abc import Callable
from tkinter import Canvas, Event, StringVar

from . import KVUtils
from .KVManager import KVManager
from .KVData import KVData

class KVInputHandler:
    def __init__(self, canvas: Canvas, kv_manager: KVManager, kv_data: KVData) -> None:
        self.resize_scheduled: bool = False
        canvas.bind("<Configure>", self.__get_on_resize(canvas, kv_manager))
        canvas.bind("<Button-1>", self.__get_on_left_click(kv_manager, kv_data))
        canvas.bind("<Button-3>", self.__get_on_right_click(kv_manager, kv_data))
        self.kv_manager = kv_manager
    
    def __get_on_resize(self, canvas: Canvas, kv_manager: KVManager) -> Callable[[Event], None]:
        def update_sizes():
            self.resize_scheduled = False
            kv_manager.update_sizes(canvas.winfo_width(), canvas.winfo_height())
        def on_resize(event: Event) -> None:
            if not self.resize_scheduled:
                #schedule resize
                canvas.after(10, update_sizes)
                self.resize_scheduled = True
        return on_resize
    
    def __get_on_left_click(self, kv_manager: KVManager, kv_data: KVData) -> Callable[[Event], None]:
        def on_left_click(event: Event) -> None:
            if (index := kv_manager.event_to_kv_index(event)) == -1:
                return
            current_indices = kv_data.get_selected_marking().indices
            if len(current_indices) == 0:
                current_indices.append(index)
            elif (different_bit := KVUtils.get_different_bit(index, current_indices)) is not None:    
                KVUtils.expand_block(current_indices, different_bit)
            else:
                return
            kv_manager.update_selected_marking()
        return on_left_click
    
    def __get_on_right_click(self, kv_manager: KVManager, kv_data: KVData) -> Callable[[Event], None]:
        def on_right_click(event: Event) -> None:
            current_marking = kv_data.get_selected_marking()
            current_indices = current_marking.indices
            if len(current_indices) == 0:
                return
            if len(current_indices) == 1:
                kv_manager.remove_marking(kv_data.selected, current_marking)
                return
            if (index := kv_manager.event_to_kv_index(event)) in current_indices:
                KVUtils.shrink_block(current_indices, index)
                kv_manager.update_selected_marking()
        return on_right_click
    
    def link_vals(self, vals: StringVar) -> None:
        def vals_changed() -> None:
            self.kv_manager.update_vals(vals.get())
        vals.trace_add('write', lambda name, index, mode: vals_changed())
    
    def link_vars(self, vars: StringVar) -> None:
        def vars_changed() -> None:
            self.kv_manager.update_vars(vars.get().split(","))
        vars.trace_add('write', lambda name, index, mode: vars_changed())