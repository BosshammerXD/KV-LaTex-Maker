from collections import deque
from collections.abc import Iterator
from itertools import count
from tkinter import Canvas, Event, StringVar

from Globals import DYNAMIC
from Globals.STATIC.DEF_KV_VALUES import VALUES
from . import KVUtils
from .KVToLaTeX import get_kv_string

from .KVData import KVData, Marking
from .KVDrawer import KVDrawer

from Shapes.KVGrid import KVGrid
from Shapes.KVIndices import KVIndices
from Shapes.KVMarkings import KVMarkings
from Shapes.KVValues import KVValues
from Shapes.KVVars import KVVars


class KVManager:
    def __init__(self, canvas: Canvas) -> None:
        self.current_col: StringVar = StringVar(value=next(iter(DYNAMIC.Colors)))
        self.__col_index = 0
        self.title = StringVar(value="")
        self.kvdata = KVData(VALUES)
        self.kvdata.markings.append(self.__build_marking())
        self.kvdata.selected = 0
        self.kvdrawer = KVDrawer(canvas, self.kvdata)

        self.grid: KVGrid = KVGrid(canvas)
        self.kv_vars: KVVars = KVVars(canvas)
        self.kv_values: KVValues = KVValues(canvas)
        self.kv_indices: KVIndices = KVIndices(canvas)
        self.kv_markings: KVMarkings = KVMarkings(canvas)

    def on_left_click(self, event: Event) -> None:  # type: ignore[no-untyped-def]
        """
        Handle left mouse button click event.
        """
        index = self.kvdrawer.canvas_to_kv_index(event.x, event.y)
        current_marking = self.kvdata.get_selected_marking()
        current_indices = current_marking.indices
        if index == -1:
            return
        if len(current_indices) == 0:
            current_indices.append(index)
        elif (different_bit := KVUtils.get_different_bit(index, current_indices)) is not None:
            KVUtils.expand_block(current_indices, different_bit)
        else:
            return

        self.kvdrawer.update_markingdata(current_marking, self.kvdata.selected)

    def on_right_click(self, event: Event) -> None:
        """
        Handle right mouse button click event.
        """
        current_marking = self.kvdata.get_selected_marking()
        current_indices = current_marking.indices
        if len(current_indices) == 0:
            return
        index = self.kvdrawer.canvas_to_kv_index(event.x, event.y)

        if index not in current_indices:
            print("Invalid click")
            return

        if len(current_indices) == 1:
            self.remove_marking(self.kvdata.selected, current_marking)
            return

        KVUtils.shrink_block(current_indices, index)
        self.kvdrawer.update_markingdata(current_marking, self.kvdata.selected)

    def get_kv_string(self) -> str:
        return get_kv_string(self.kvdata, self.title.get())


    def __build_marking(self) -> Marking:
        latex_col: str = self.current_col.get()
        tk_col: str = DYNAMIC.Colors[latex_col]
        return Marking(latex_col, tk_col, KVManager.__gen_marking_id())

    def new_marking(self) -> None:
        current_indices = self.kvdata.get_selected_marking().indices
        if len(current_indices) == 0:
            return

        self.__col_index += 1
        if self.__col_index >= len(DYNAMIC.Colors):
            self.__col_index = 0
        self.current_col.set(list(DYNAMIC.Colors.keys())[self.__col_index])
        
        self.kvdata.selected += 1
        self.kvdata.markings.insert(self.kvdata.selected, self.__build_marking())
        self.kvdrawer.kv_markings.update_marking(self.kvdata.selected, self.kvdata.get_selected_marking())
        self.kvdrawer.kv_markings.update_selected(self.kvdata.selected)
        

    def different_marking(self, offset: int) -> None:
        current_indices = self.kvdata.get_selected_marking().indices
        if len(current_indices) == 0 and len(self.kvdata.markings) > 1:
            self.remove_marking(
                self.kvdata.selected,
                self.kvdata.get_selected_marking()
            )
            self.kvdata.markings.pop(self.kvdata.selected)
        else:
            self.kvdata.selected += offset

        marking_len = len(self.kvdata.markings)
        while self.kvdata.selected < 0:
            self.kvdata.selected += marking_len
        while self.kvdata.selected >= marking_len:
            self.kvdata.selected -= marking_len
        val = self.kvdata.get_selected_marking().latex_color

        self.current_col.set(val)
        self.kvdrawer.kv_markings.update_selected(self.kvdata.selected)

    
    def update_markings(self) -> None:
        """
        Removes all Markings that have a color that no longer exists
        """
        #TODO: update so it works with the new system
        self.kvdata.markings = [
            m for m in self.kvdata.markings if m.latex_color in DYNAMIC.Colors.keys()
        ]
        if len(self.kvdata.markings):
            col = self.kvdata.markings[0].latex_color
            self.current_col.set(col)
            self.kvdata.selected = 0
            self.kvdrawer.draw_all()
        else:
            self.kvdata.selected = 0
            self.current_col.set(DYNAMIC.Colors.__iter__().__next__())
            self.kvdata.markings.append(self.__build_marking())
    
    def remove_marking(self, index: int, marking: Marking):
        marking.indices.clear()
        self.kvdrawer.kv_markings.update_marking(index, marking)
        self.__remove_marking_id(marking.tag)
    
    __MARKING_PREFIX: str = "marking_"
    __free_ids: deque[int] = deque()
    __counter: Iterator[int] = count()

    @classmethod
    def __gen_marking_id(cls) -> str:
        if cls.__free_ids:
            n = cls.__free_ids.popleft()
        else:
            n = next(cls.__counter)
        return f"{cls.__MARKING_PREFIX}{n}"
    
    @classmethod
    def __remove_marking_id(cls, id_str: str) -> None:
        if not id_str.startswith(cls.__MARKING_PREFIX):
            return
        try:
            n = int(id_str[len(cls.__MARKING_PREFIX):])
        except ValueError:
            return
        if n >= 0 and n not in cls.__free_ids:
            cls.__free_ids.append(n)
    
    def update_sizes(self, width: int, height: int) -> None:
        """
        Update the sizes of the cells based on the current canvas size.
        """
        self.__width = width
        self.__height = height
        if self.kvdata.get_num_vars() == 0:
            return
        
        num_left_vars = self.kvdata.get_num_vars() // 2
        num_top_vars = self.kvdata.get_num_vars() - num_left_vars

        self.kvdata.width = 2**num_top_vars
        self.kvdata.height = 2**num_left_vars

        self.kv_vars.update(self.kvdata.vars)
        self.grid.update(self.kvdata.width, self.kvdata.height)
        self.kv_values.update(self.kvdata.vals)
        self.kv_indices.update(2**self.kvdata.get_num_vars())
        self.draw_all()
    
    def draw_all(self) -> None:
        if self.kvdata.get_num_vars() == 0:
            return
        self.grid.draw(self.__width, self.__height)
        self.kv_vars.draw(self.grid)
        self.kv_values.draw(self.grid)
        self.kv_indices.draw(self.grid)
        self.kv_markings.draw(self.grid, self.kvdata.markings)
    
    def event_to_kv_index(self, event: Event) -> int:
        """
        Convert canvas coordinates to Karnaugh map index.
        """
        new_x: int = int((event.x - self.grid.x_offset) // self.grid.cell_size)
        new_y: int = int((event.y - self.grid.y_offset) // self.grid.cell_size)

        if new_x < 0 or new_x >= self.kvdata.width or new_y < 0 or new_y >= self.kvdata.height:
            return -1

        return KVUtils.CoordinateToIndex(new_x, new_y)
    
    def update_selected_marking(self):
        marking = self.kvdata.get_selected_marking()
        marking.drawables = self.kvdrawer.indices_to_markingdata(marking.indices)
        self.kv_markings.update_marking(self.kvdata.selected, marking)
        self.kv_markings.update_selected(self.kvdata.selected)
        self.kv_markings.draw_marking(self.grid, self.kvdata.selected, marking)
    
    def update_vals(self, new_vals: str) -> None:
        self.kvdata.vals = new_vals
        self.kv_values.update(new_vals)
        self.kv_values.draw(self.grid)
    
    def update_vars(self, new_vars: list[str]) -> None:
        if new_vars != self.kvdata.vars:
            self.kvdata.vars = new_vars
            num_left_vars = self.kvdata.get_num_vars() // 2
            num_top_vars = self.kvdata.get_num_vars() - num_left_vars

            self.kvdata.width = 2**num_top_vars
            self.kvdata.height = 2**num_left_vars
            self.grid.update(self.kvdata.width, self.kvdata.height)
            self.kv_vars.update(new_vars)
            self.kv_indices.update(2**self.kvdata.get_num_vars())
            self.grid.draw(self.__width, self.__height)
            self.kv_vars.draw(self.grid)
            self.kv_values.draw(self.grid)
            self.kv_indices.draw(self.grid)