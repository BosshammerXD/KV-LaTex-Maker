from itertools import count
from tkinter import Canvas, Event, StringVar

from Globals import DYNAMIC
import IterTools
from . import KVUtils
from .KVToLaTeX import get_kv_string

from .Dataclasses.KVData import KVData
from .Dataclasses.Edge import Edge
from .Dataclasses.Marking import Marking, MarkingData

from Shapes.KVGrid import KVGrid
from Shapes.KVIndices import KVIndices
from Shapes.KVMarkings import KVMarkings
from Shapes.KVValues import KVValues
from Shapes.KVVars import KVVars

from enum import IntFlag

class KVFlags(IntFlag):
    NONE = 0
    GRID = 1
    VARS = 2
    VALS = 4
    IDXS = 8
    ALL = 15

class KVManager:
    __MARKING_PREFIX: str = "marking_"
    def __init__(self, canvas: Canvas) -> None:
        self.__kv_grid: KVGrid = KVGrid(canvas)
        self.__kv_vars: KVVars = KVVars(canvas)
        self.__kv_values: KVValues = KVValues(canvas)
        self.__kv_indices: KVIndices = KVIndices(canvas)
        self.__kv_markings: KVMarkings = KVMarkings(canvas)

        self.__marking_id_generator = IterTools.IDGenerator(map(lambda x: f"{KVManager.__MARKING_PREFIX}{x}", count()))
        self.__colors: IterTools.CyclicCache[str] = IterTools.CyclicCache(iter(DYNAMIC.Colors))
        self.current_col: StringVar = StringVar(value=self.__colors.get_item())
        self.title = StringVar(value="")
        self.__kv_data = KVData(self.__kv_markings)
        self.__kv_data.add_marking(self.current_col.get(), self.__marking_id_generator.generate_id())
        self.__kv_data.selected = 0
        self.draw_flags: KVFlags = KVFlags.NONE
        self.__width = canvas.winfo_width()
        self.__height = canvas.winfo_height()

    def get_selected_marking(self) -> Marking:
        return self.__kv_data.get_selected_marking()

    def get_kv_string(self) -> str:
        return get_kv_string(self.__kv_data, self.title.get())

    def color_changed(self, new_color: str):
        if self.__kv_data.len_markings:
            marking = self.__kv_data.get_selected_marking()
            marking.latex_color = new_color
            self.__kv_markings.set_color(marking.TAG, marking.tkinter_color)

    def new_marking(self) -> None:
        new_col = self.__colors.get_item()
        
        self.__kv_data.add_marking(new_col, self.__marking_id_generator.generate_id(), self.__kv_data.selected + 1)
        self.__kv_data.selected += 1
        self.current_col.set(new_col)
        

    def different_marking(self, offset: int) -> None:
        current_marking = self.__kv_data.get_selected_marking()
        current_indices = current_marking.indices
        if len(current_indices) == 0 and self.__kv_data.len_markings > 1:
            self.clear_marking(current_marking)
            self.__kv_data.remove_marking(self.__kv_data.selected)
            self.__colors.release_item(current_marking.latex_color)
        else:
            self.__kv_data.selected += offset

        self.current_col.set(current_marking.latex_color)

    
    def update_markings(self) -> None:
        """
        Removes all Markings that have a color that no longer exists
        """
        self.__kv_data.update_colors()
        if not self.__kv_data.len_markings:
            self.current_col.set(next(iter(DYNAMIC.Colors)))
            self.__kv_data.add_marking(self.current_col.get(), self.__marking_id_generator.generate_id())
            self.__kv_data.selected = 0
        self.__colors.change_generator(iter(DYNAMIC.Colors), self.current_col.get())


    def clear_marking(self, marking: Marking):
        marking.indices.clear()
        self.update(changed_markings=[marking])
        self.__marking_id_generator.release_id(marking.TAG)
    
    def draw(self, markings: list[Marking] = []) -> None:
        if self.__kv_data.get_num_vars() == 0:
            return
        if KVFlags.GRID in self.draw_flags:
            self.__kv_grid.draw(self.__width, self.__height)
        if KVFlags.VARS in self.draw_flags:
            self.__kv_vars.draw(self.__kv_grid)
        if KVFlags.VALS in self.draw_flags:
            self.__kv_values.draw(self.__kv_grid)
        if KVFlags.IDXS in self.draw_flags:
            self.__kv_indices.draw(self.__kv_grid)
        if markings:
            [self.__kv_markings.draw_marking(self.__kv_grid, m) for m in markings]
        self.draw_flags = KVFlags.NONE
    
    def update(self, new_vars: list[str] = [], new_values: str = "", changed_markings: list[Marking] = [], new_dim: tuple[int, int] = (-1, -1)) -> None:
        draw_grid: bool = new_dim[0] >= 0 and new_dim[1] >= 0
        if new_vars and new_vars != self.__kv_data.vars:
            draw_grid |= len(self.__kv_data.vars) != len(new_vars)
            self.__kv_data.vars = new_vars
            self.__kv_vars.update(new_vars)
            self.draw_flags |= KVFlags.VARS
        if draw_grid:
            self.update_kv_width(new_dim)
            self.__kv_grid.update(self.__kv_data.width, self.__kv_data.height)
            self.__kv_indices.update(2**self.__kv_data.get_num_vars())
            self.draw_flags |= KVFlags.ALL
        if new_values:
            self.__kv_data.vals = new_values
            self.__kv_values.update(new_values)
            self.draw_flags |= KVFlags.VALS
        if changed_markings:
            [self.__kv_markings.update_marking(m) for m in changed_markings]
            self.draw(changed_markings)
        else:
            self.draw()

    
    def event_to_kv_index(self, event: Event) -> int:
        """
        Convert canvas coordinates to Karnaugh map index.
        """
        new_x: int = int((event.x - self.__kv_grid.x_offset) // self.__kv_grid.cell_size)
        new_y: int = int((event.y - self.__kv_grid.y_offset) // self.__kv_grid.cell_size)

        if new_x < 0 or new_x >= self.__kv_data.width or new_y < 0 or new_y >= self.__kv_data.height:
            return -1

        return KVUtils.CoordinateToIndex(new_x, new_y)
    
    def update_selected_marking(self):
        marking = self.__kv_data.get_selected_marking()
        marking.drawables = self.indices_to_markingdata(marking.indices)
        self.update(changed_markings=[marking])
    
    def update_kv_width(self, new_dim: tuple[int, int]) -> None:
        if new_dim[0] >= 0 and new_dim[1] >= 0:
            self.__width, self.__height = new_dim
        num_left_vars = self.__kv_data.get_num_vars() // 2
        num_top_vars = self.__kv_data.get_num_vars() - num_left_vars

        self.__kv_data.width = 2**num_top_vars
        self.__kv_data.height = 2**num_left_vars

    def indices_to_markingdata(self, indices: list[int]) -> list[MarkingData]:
        idx_set: set[int] = set(indices)
        ret: list[MarkingData] = []
        kv_max_x = self.__kv_data.width - 1
        kv_max_y = self.__kv_data.height - 1
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2) = self.__get_rect_bounds(block)
            openings: Edge = Edge.NONE
            if not(x1 == 0 and KVUtils.CoordinateToIndex(kv_max_x, y1) in idx_set):
                openings |= Edge.LEFT
            if not(x2 == self.__kv_data.width and KVUtils.CoordinateToIndex(0, y1) in idx_set):
                openings |= Edge.RIGHT
            if Edge.LEFT not in openings and Edge.RIGHT not in openings:
                openings |= Edge.RIGHT | Edge.LEFT

            if not(y1 == 0 and KVUtils.CoordinateToIndex(x1, kv_max_y) in idx_set):
                openings |= Edge.TOP
            if not(y2 == self.__kv_data.height and KVUtils.CoordinateToIndex(x1, 0) in idx_set):
                openings |= Edge.BOTTOM
            if Edge.TOP not in openings and Edge.BOTTOM not in openings:
                openings |= Edge.TOP | Edge.BOTTOM
            
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret
    
    def __get_rect_bounds(self, block: list[tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
        xs, ys = zip(*block)
        min_x, max_x = min(xs), max(xs) + 1
        min_y, max_y = min(ys), max(ys) + 1

        return ((min_x, min_y), (max_x, max_y))