from itertools import count
from tkinter import Canvas, Event, StringVar

import IterTools
from KV_Diagramm import KVUtils
from KV_Diagramm.KVDrawer import GridUpdateMode, KVDrawer
from UI.KVColorsMenu import KVColorsMenu
from .KVToLaTeX import get_kv_string

from .Dataclasses.KVData import KVData
from .Dataclasses.Marking import Marking, MarkingData

from Shapes.KVMarkings import KVMarkings

class KVManager:
    __MARKING_PREFIX: str = "marking_"
    def __init__(self, canvas: Canvas) -> None:
        kv_markings = KVMarkings(canvas)
        self.__kv_drawer = KVDrawer(canvas, kv_markings)
        self.__kv_data = KVData(kv_markings)

        self.__marking_id_generator = IterTools.IDGenerator(map(lambda x: f"{KVManager.__MARKING_PREFIX}{x}", count()))

        self.title = StringVar(value="")

    def get_kv_string(self) -> str:
        return get_kv_string(self.__kv_data, self.title.get())
    #region Button Funcs
    def new_marking(self) -> None:
        if len(self.__kv_data.get_selected_marking().indices) == 0:
            return #why would someone need a new marking if the current one is empty
        new_col = self.__color_menu.next_color()
        
        self.__kv_data.add_marking(new_col, self.__marking_id_generator.generate_id(), self.__kv_data.selected + 1)
        self.__kv_data.selected += 1

    def different_marking(self, offset: int) -> None:
        current_marking = self.__kv_data.get_selected_marking()
        current_indices = current_marking.indices
        if len(current_indices) == 0 and self.__kv_data.len_markings > 1:
            self.__clear_marking(current_marking)
            self.__kv_data.remove_marking(self.__kv_data.selected)
            self.__color_menu.release_marking_color(current_marking)
            self.__marking_id_generator.release_id(current_marking.TAG)
        else:
            self.__kv_data.selected += offset

        self.__color_menu.set_color_from_marking(self.__kv_data.get_selected_marking())
    #endregion
    #
    #
    #
    #region Events
    def on_resize(self, event: Event) -> None:
        self.__kv_drawer.schedule_resize(self.__kv_data)

    def on_left_click(self, event: Event) -> None:
        if (index := self.__event_to_kv_index(event)) == -1:
            return
        current_indices = self.__kv_data.get_selected_marking().indices
        if len(current_indices) == 0:
            current_indices.append(index)
        elif (different_bit := KVUtils.get_different_bit(index, current_indices)) is not None:    
            KVUtils.expand_block(current_indices, different_bit)
        else:
            return
        self.__update_selected_marking()
    
    def on_right_click(self, event: Event) -> None:
        current_marking = self.__kv_data.get_selected_marking()
        current_indices = current_marking.indices
        if len(current_indices) == 0:
            return
        elif len(current_indices) == 1:
            self.__clear_marking(current_marking)
        elif (index := self.__event_to_kv_index(event)) in current_indices:
            KVUtils.shrink_block(current_indices, index)
            self.__update_selected_marking()
    
    def on_colors_changed(self, event: Event) -> None:
        self.__kv_data.update_colors()
        generate_new_color: bool = not self.__kv_data.len_markings
        self.__color_menu.update_options(generate_new_color)
        if generate_new_color:
            self.__kv_data.add_marking(self.__color_menu.get_color(), self.__marking_id_generator.generate_id())
            self.__kv_data.selected = 0
    #endregion
    #
    #
    #
    #region linker methods 
    def link_vals(self, vals: StringVar) -> None:
        def vals_changed() -> None:
            new_values = vals.get()
            self.__kv_data.vals = new_values
            self.__kv_drawer.update(self.__kv_data, new_values=new_values)
        vals.trace_add('write', lambda name, index, mode: vals_changed())
        vals_changed()
    
    def link_vars(self, vars: StringVar) -> None:
        def vars_changed() -> None:
            new_vars = vars.get().split(",")
            if len(self.__kv_data.vars) != len(new_vars):    
                grid_mode: GridUpdateMode = GridUpdateMode.UPDATE
            else:
                grid_mode: GridUpdateMode = GridUpdateMode.NONE
            self.__kv_data.vars = new_vars
            self.__update_kv_width()
            self.__kv_drawer.update(self.__kv_data, new_vars=new_vars, draw_grid=grid_mode)
        vars.trace_add('write', lambda name, index, mode: vars_changed())
        vars_changed()
    
    def link_marking_color(self, color_menu: KVColorsMenu) -> None:
        color_menu.trace_color(self.__color_changed)
        self.__color_menu: KVColorsMenu = color_menu
        self.__kv_data.add_marking(color_menu.get_color(), self.__marking_id_generator.generate_id())
        self.__kv_data.selected = 0
    
    def __color_changed(self, new_color: str):
        if self.__kv_data.len_markings:
            marking = self.__kv_data.get_selected_marking()
            marking.latex_color = new_color
            self.__kv_drawer.set_marking_color(marking.TAG, marking.tkinter_color)
    #endregion
    #
    #
    #
    #region Internal Utils
    def __event_to_kv_index(self, event: Event):
        x,y = self.__kv_drawer.canvas_to_grid_coord(event.x, event.y)
        if x < 0 or x >= self.__kv_data.width or y < 0 or y >= self.__kv_data.height:
            return -1
        return KVUtils.CoordinateToIndex(x,y)
    
    def __update_kv_width(self) -> None:
        num_left_vars = self.__kv_data.get_num_vars() // 2
        num_top_vars = self.__kv_data.get_num_vars() - num_left_vars

        self.__kv_data.width = 2**num_top_vars
        self.__kv_data.height = 2**num_left_vars
    
    def __clear_marking(self, marking: Marking):
        marking.indices.clear()
        self.__kv_drawer.delete_marking(marking.TAG)
    
    def __update_selected_marking(self):
        marking = self.__kv_data.get_selected_marking()
        marking.drawables = MarkingData.from_indices(marking.indices, self.__kv_data.width, self.__kv_data.height)
        self.__kv_drawer.update(self.__kv_data, changed_markings=[marking])
    #endregion