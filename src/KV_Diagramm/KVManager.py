from itertools import count
from tkinter import Canvas, Event, StringVar

import IterTools
from KV_Diagramm import KVUtils
from KV_Diagramm.KVDrawer import GridUpdateMode, KVDrawer
from UI.KVColorsMenu import KVColorsMenu
from .KVToLaTeX import get_kv_string

from .Dataclasses.KVData import KVData
from .Dataclasses.Marking import Marking, MarkingData

from Globals.STATIC import MAIN_UNDO_MANAGER
from UndoManager import ActionTypes

from Shapes.KVMarkings import KVMarkings

from collections.abc import Callable
from typing import TypeVar, Any

_RET_T = TypeVar("_RET_T")

def lazy(func:Callable[..., _RET_T]) -> Callable[..., Callable[[], _RET_T]]:
    def my_inner(*args: list[Any], **kwds: dict[str, Any]) -> Callable[[], _RET_T]:
        return lambda: func(*args, **kwds)
    return my_inner

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
            return #why would someone need a new marking if the current one is 
        new_col = self.__color_menu.next_color()
        
        self.__kv_data.add_marking(new_col, self.__marking_id_generator.generate_id(), self.__kv_data.selected + 1)
        self.__kv_data.selected += 1
        current_marking = self.__kv_data.get_selected_marking()
        current_index = self.__kv_data.selected    
        def action(typ: ActionTypes) -> None:
            match typ:
                case ActionTypes.DO_ACTION:
                    self.__restore_marking(current_marking, current_index)
                    self.__kv_data.selected = current_index
                case ActionTypes.UNDO_ACTION:
                    self.__forget_marking(current_marking, current_index)
                    self.__kv_data.selected = current_index - 1
                case ActionTypes.CLEARED_FROM_REDO:
                    self.__marking_id_generator.release_id(current_marking.TAG)
                case _: pass
        MAIN_UNDO_MANAGER.add_action(action,execute_do=False)

    def different_marking(self, offset: int) -> None:
        current_marking = self.__kv_data.get_selected_marking()
        delete_old: bool = len(current_marking.indices) == 0 and self.__kv_data.len_markings > 1
        current_index = self.__kv_data.selected
        if delete_old:
            def action(typ: ActionTypes) -> None:
                match typ:
                    case ActionTypes.DO_ACTION:
                        self.__forget_marking(current_marking, current_index)
                    case ActionTypes.UNDO_ACTION:
                        self.__restore_marking(current_marking, current_index)
                    case ActionTypes.PUSHED_OUT_OF_QUEUE:
                        self.__marking_id_generator.release_id(current_marking.TAG)
                    case _: pass
        else:
            def action(typ: ActionTypes) -> None:
                match typ:
                    case ActionTypes.DO_ACTION:
                        self.__kv_data.selected += offset
                    case ActionTypes.UNDO_ACTION:
                        self.__kv_data.selected -= offset
                    case _: return
        MAIN_UNDO_MANAGER.add_action(action, execute_do=True)
    #endregion
    #
    #
    #
    #region Events
    def on_resize(self, event: Event) -> None:
        self.__kv_drawer.schedule_resize(self.__kv_data)

    def on_left_click(self, event: Event) -> None:
        if (index := self.__event_to_kv_index(event.x, event.y)) == -1:
            return
        current_marking = self.__kv_data.get_selected_marking()
        if KVUtils.get_different_bit(index, current_marking.indices) is not None or len(current_marking.indices) == 0:
            action =MAIN_UNDO_MANAGER.make_action(self.__expand_marking(current_marking, index), self.__shrink_marking(current_marking, index))
            MAIN_UNDO_MANAGER.add_action(action, execute_do=True)
    
    def on_right_click(self, event: Event) -> None:
        current_marking = self.__kv_data.get_selected_marking()
        if len(current_marking.indices) == 0:
            return
        index = self.__event_to_kv_index(event.x, event.y)
        if index in current_marking.indices:
            action = MAIN_UNDO_MANAGER.make_action(self.__shrink_marking(current_marking, index), self.__expand_marking(current_marking, index))
            MAIN_UNDO_MANAGER.add_action(action, execute_do=True)
    
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
        @self.__traced_action(vals, self.__kv_data.vals)
        def vals_changed(new_values: str) -> None:
            self.__kv_data.vals = new_values
            self.__kv_drawer.update(self.__kv_data, new_values=new_values)
        vals.trace_add('write', lambda name, index, mode: vals_changed())
        vals_changed()
    
    def link_vars(self, vars: StringVar) -> None:
        @self.__traced_action(vars, ",".join(self.__kv_data.vars))
        def vars_changed(new_vars: str) -> None:
            new_vars_ls = new_vars.split(",")
            if len(self.__kv_data.vars) != len(new_vars):    
                grid_mode: GridUpdateMode = GridUpdateMode.UPDATE
            else:
                grid_mode: GridUpdateMode = GridUpdateMode.NONE
            self.__kv_data.vars = new_vars_ls
            self.__update_kv_width()
            self.__kv_drawer.update(self.__kv_data, new_vars=new_vars_ls, draw_grid=grid_mode)
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
            old_color = marking.latex_color
            def action(typ: ActionTypes) -> None:
                match typ:
                    case ActionTypes.DO_ACTION:
                        marking.latex_color = new_color
                        self.__color_menu.set_color_no_trace(new_color)
                    case ActionTypes.UNDO_ACTION:
                        marking.latex_color = old_color
                        self.__color_menu.set_color_no_trace(old_color)
                    case _: return
                self.__kv_drawer.set_marking_color(marking.TAG, marking.tkinter_color)
            MAIN_UNDO_MANAGER.add_action(action, execute_do=True)
    #endregion
    #
    #
    #
    #region Internal Utils
    def __traced_action(self, var: StringVar, old_val: str) -> Callable[[Callable[[str], None]], Callable[[], None]]:
        no_action: bool = False
        def decorator(f: Callable[[str], None]) -> Callable[[], None]:
            def action_register() -> None:
                nonlocal no_action
                new_val = var.get()
                f(new_val)
                def action(typ: ActionTypes) -> None:
                    nonlocal no_action
                    match typ:
                        case ActionTypes.DO_ACTION:
                            no_action = True
                            var.set(old_val)
                        case ActionTypes.UNDO_ACTION:
                            no_action = True
                            var.set(new_val)
                        case _: return
                if not no_action:
                    MAIN_UNDO_MANAGER.add_action(action, execute_do=False)
                else:
                    no_action = False
            return action_register
        return decorator



    def __event_to_kv_index(self, event_x: int, event_y: int):
        x,y = self.__kv_drawer.canvas_to_grid_coord(event_x, event_y)
        if x < 0 or x >= self.__kv_data.width or y < 0 or y >= self.__kv_data.height:
            return -1
        return KVUtils.CoordinateToIndex(x,y)
    
    def __update_kv_width(self) -> None:
        num_left_vars = self.__kv_data.get_num_vars() // 2
        num_top_vars = self.__kv_data.get_num_vars() - num_left_vars

        self.__kv_data.width = 2**num_top_vars
        self.__kv_data.height = 2**num_left_vars
    
    def __restore_marking(self, marking: Marking, marking_index: int) -> None:
        self.__kv_data.restore_marking(marking, marking_index)

    def __forget_marking(self, marking: Marking, marking_index: int) -> None:
        self.__clear_marking(marking)
        self.__kv_data.remove_marking(marking_index)
        self.__color_menu.release_marking_color(marking)

    @lazy
    def __shrink_marking(self, marking: Marking, excluded_index: int):
        if len(marking.indices) == 1:
            self.__clear_marking(marking)
        elif excluded_index in marking.indices:
            KVUtils.shrink_block(marking.indices, excluded_index)
            self.__update_marking(marking)

    @lazy
    def __expand_marking(self, marking: Marking, added_index: int):
        if len(marking.indices) == 0:
            marking.indices.append(added_index)
        elif (diff_bit := KVUtils.get_different_bit(added_index, marking.indices)) is not None:
            KVUtils.expand_block(marking.indices, diff_bit)
        self.__update_marking(marking)

    def __clear_marking(self, marking: Marking) -> None:
        marking.indices = []
        self.__kv_drawer.delete_marking(marking.TAG)
    
    def __update_marking(self, marking: Marking) -> None:
        marking.drawables = MarkingData.from_indices(marking.indices, self.__kv_data.width, self.__kv_data.height)
        self.__kv_drawer.update(self.__kv_data, changed_markings=[marking])
    #endregion