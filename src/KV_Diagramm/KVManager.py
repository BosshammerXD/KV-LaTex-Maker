from collections.abc import Iterator
from itertools import count, cycle
from tkinter import Canvas, Event, StringVar

from Globals import DYNAMIC
from Globals.STATIC.DEF_KV_VALUES import VALUES, VARS
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


class KVManager:
    __MARKING_PREFIX: str = "marking_"
    def __init__(self, canvas: Canvas) -> None:
        self.__kv_grid: KVGrid = KVGrid(canvas)
        self.__kv_vars: KVVars = KVVars(canvas)
        self.__kv_values: KVValues = KVValues(canvas)
        self.__kv_indices: KVIndices = KVIndices(canvas)
        self.__kv_markings: KVMarkings = KVMarkings(canvas)

        self.__marking_id_generator = IterTools.IDGenerator(map(lambda x: f"{KVManager.__MARKING_PREFIX}{x}", count()))
        self.__colors: Iterator[str] = cycle(iter(DYNAMIC.Colors))
        self.current_col: StringVar = StringVar(value=next(self.__colors))
        self.title = StringVar(value="")
        self.__kv_data = KVData(self.__kv_markings, VALUES, VARS.split(","))
        self.__kv_data.add_marking(self.current_col.get(), self.__marking_id_generator.generate_id())
        self.__kv_data.selected = 0

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
        current_indices = self.__kv_data.get_selected_marking().indices
        if len(current_indices) == 0:
            return

        new_col = next(self.__colors)
        
        self.__kv_data.add_marking(new_col, self.__marking_id_generator.generate_id(), self.__kv_data.selected + 1)
        self.__kv_data.selected += 1
        self.__kv_markings.update_selected(self.__kv_data.selected)
        self.current_col.set(new_col)
        

    def different_marking(self, offset: int) -> None:
        current_indices = self.__kv_data.get_selected_marking().indices
        if len(current_indices) == 0 and self.__kv_data.len_markings > 1:
            self.remove_marking(
                self.__kv_data.selected,
                self.__kv_data.get_selected_marking()
            )
            self.__kv_data.remove_marking(self.__kv_data.selected)
        else:
            self.__kv_data.selected += offset

        self.current_col.set(self.__kv_data.get_selected_marking().latex_color)
        self.__kv_markings.update_selected(self.__kv_data.selected)

    
    def update_markings(self) -> None:
        """
        Removes all Markings that have a color that no longer exists
        """
        self.__kv_data.update_colors()
        if not self.__kv_data.len_markings:
            self.current_col.set(DYNAMIC.Colors.__iter__().__next__())
            self.__kv_data.add_marking(self.current_col.get(), self.__marking_id_generator.generate_id())
            self.__kv_data.selected = 0
        #TODO: update so it works with the new system
        #self.__kvdata.markings = [
        #    m for m in self.__kvdata.markings if m.latex_color in DYNAMIC.Colors.keys()
        #]
        #if len(self.__kvdata.markings):
        #    col = self.__kvdata.markings[0].latex_color
        #    self.current_col.set(col)
        #    self.__kvdata.selected = 0
        #    self.draw_all()
        #else:
        #    self.__kvdata.selected = 0
        #    self.current_col.set(DYNAMIC.Colors.__iter__().__next__())
        #    self.__kvdata.markings.append(self.__build_marking())
    
    def remove_selected_marking(self):
        self.remove_marking(self.__kv_data.selected, self.__kv_data.get_selected_marking())

    def remove_marking(self, index: int, marking: Marking):
        marking.indices.clear()
        self.__kv_markings.update_marking(index, marking)
        self.__marking_id_generator.release_id(marking.TAG)
    
    def update_sizes(self, width: int, height: int) -> None:
        """
        Update the sizes of the cells based on the current canvas size.
        """
        self.__width = width
        self.__height = height
        if self.__kv_data.get_num_vars() == 0:
            return
        
        num_left_vars = self.__kv_data.get_num_vars() // 2
        num_top_vars = self.__kv_data.get_num_vars() - num_left_vars

        self.__kv_data.width = 2**num_top_vars
        self.__kv_data.height = 2**num_left_vars

        self.__kv_vars.update(self.__kv_data.vars)
        self.__kv_grid.update(self.__kv_data.width, self.__kv_data.height)
        self.__kv_values.update(self.__kv_data.vals)
        self.__kv_indices.update(2**self.__kv_data.get_num_vars())
        self.draw_all()
    
    def draw_all(self) -> None:
        if self.__kv_data.get_num_vars() == 0:
            return
        self.__kv_grid.draw(self.__width, self.__height)
        self.__kv_vars.draw(self.__kv_grid)
        self.__kv_values.draw(self.__kv_grid)
        self.__kv_indices.draw(self.__kv_grid)
        self.__kv_markings.draw(self.__kv_grid, self.__kv_data.markings)
    
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
        self.__kv_markings.update_marking(self.__kv_data.selected, marking)
        self.__kv_markings.draw_marking(self.__kv_grid, marking)
    
    def update_vals(self, new_vals: str) -> None:
        self.__kv_data.vals = new_vals
        self.__kv_values.update(new_vals)
        self.__kv_values.draw(self.__kv_grid)
    
    def update_vars(self, new_vars: list[str]) -> None:
        if new_vars != self.__kv_data.vars:
            self.__kv_data.vars = new_vars
            num_left_vars = self.__kv_data.get_num_vars() // 2
            num_top_vars = self.__kv_data.get_num_vars() - num_left_vars

            self.__kv_data.width = 2**num_top_vars
            self.__kv_data.height = 2**num_left_vars
            self.__kv_grid.update(self.__kv_data.width, self.__kv_data.height)
            self.__kv_vars.update(new_vars)
            self.__kv_indices.update(2**self.__kv_data.get_num_vars())
            self.__kv_grid.draw(self.__width, self.__height)
            self.__kv_vars.draw(self.__kv_grid)
            self.__kv_values.draw(self.__kv_grid)
            self.__kv_indices.draw(self.__kv_grid)
    
    def indices_to_markingdata(self, indices: list[int]) -> list[MarkingData]:
        ret: list[MarkingData] = []
        kv_max_x = self.__kv_data.width - 1
        kv_max_y = self.__kv_data.height - 1
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2) = self.__get_rect_bounds(block)
            openings: Edge = Edge.NONE
            if not(x1 == 0 and KVUtils.CoordinateToIndex(kv_max_x, y1) in indices):
                openings |= Edge.LEFT
            if not(x2 == self.__kv_data.width and KVUtils.CoordinateToIndex(0, y1) in indices):
                openings |= Edge.RIGHT
            if Edge.LEFT not in openings and Edge.RIGHT not in openings:
                openings |= Edge.RIGHT | Edge.LEFT

            if not(y1 == 0 and KVUtils.CoordinateToIndex(x1, kv_max_y) in indices):
                openings |= Edge.TOP
            if not(y2 == self.__kv_data.height and KVUtils.CoordinateToIndex(x1, 0) in indices):
                openings |= Edge.BOTTOM
            if Edge.TOP not in openings and Edge.BOTTOM not in openings:
                openings |= Edge.TOP | Edge.BOTTOM
            
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret
    
    def __get_rect_bounds(self, block: list[int]) -> tuple[tuple[int, int], tuple[int, int]]:
        coords = [KVUtils.IndexToCoordinate(i) for i in block]
        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs) + 1
        min_y, max_y = min(ys), max(ys) + 1

        return ((min_x, min_y), (max_x, max_y))