from dataclasses import dataclass
from functools import reduce
from tkinter import Canvas, Event
from typing import Callable, Optional

from .KVData import Edge, KVData, Marking, MarkingData
from . import KVUtils
from Globals.STATIC import FONTS

@dataclass
class GridData:
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    cell_size: float = 0
    def get_end_x(self) -> float:
        return self.x + self.width
    def get_end_y(self) -> float:
        return self.y + self.height
    
    def grid_to_canvas_coord(self, x: float, y: float) -> tuple[float, float]:
        return x * self.cell_size + self.x, y * self.cell_size + self.y
    
    def grid_to_canvas_x(self, x: float) -> float:
        return x * self.cell_size + self.x
    
    def grid_to_canvas_y(self, y: float) -> float:
        return y * self.cell_size + self.y
    
    

class KVDrawer:
    def __init__(self, canvas: Canvas, kvdata: KVData) -> None:
        self.__canvas = canvas
        self.__kvdata = kvdata

        self.__grid: GridData = GridData()

        canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event: Event) -> None: #type: ignore[no-untyped-def]
        """
        Handle window resize event.
        """
        self.update_sizes()
        self.draw()

    def update_sizes(self) -> None:
        """
        Update the sizes of the cells based on the current canvas size.
        """
        self.__width = int(self.__canvas.winfo_width())
        self.__height = int(self.__canvas.winfo_height())
        if self.__kvdata.get_num_vars() == 0:
            return
        
        num_left_vars = self.__kvdata.get_num_vars() // 2
        num_top_vars = self.__kvdata.get_num_vars() - num_left_vars

        self.__kvdata.dimensions = (2**num_top_vars, 2**num_left_vars)

        cell_width = self.__width / (self.__kvdata.dimensions[0] + num_top_vars)
        cell_height = self.__height / (self.__kvdata.dimensions[1] + num_left_vars)

        self.__grid.cell_size = min(cell_width, cell_height)

        self.__large_font = (FONTS.TYPE, int(self.__grid.cell_size // 2))
        self.__normal_font = (FONTS.TYPE, int(self.__grid.cell_size // 4))
        self.__small_font = (FONTS.TYPE, int(self.__grid.cell_size // 6))

        self.__grid.width = self.__grid.cell_size * self.__kvdata.dimensions[0]
        self.__grid.height = self.__grid.cell_size * self.__kvdata.dimensions[1]
        self.__grid.x = (self.__width - self.__grid.width) / 2
        self.__grid.y = (self.__height - self.__grid.height) / 2

        self.draw()

    def draw(self) -> None:
        self.__canvas.delete("all")
        if self.__kvdata.get_num_vars() == 0:
            return
        
        self.__draw_grid()

        self.__draw_vars()

        self.__draw_markings()
        
        self.__draw_vals_and_indices()

    def __draw_grid(self) -> None:
        """
        Draw lines on the canvas.
        """
        for c in range(1, self.__kvdata.dimensions[0]):
            x = self.__grid.grid_to_canvas_x(c)
            self.__canvas.create_line(
                x, self.__grid.y, x, self.__grid.y + self.__grid.height)
        for r in range(1, self.__kvdata.dimensions[1]):
            y = self.__grid.grid_to_canvas_y(r)
            self.__canvas.create_line(
                self.__grid.x, y, self.__grid.x + self.__grid.width, y)

    def __draw_vars(self):
        """
        Draws the variables above and left of the grid
        """
        for index, var in enumerate(self.__kvdata.vars):
            layer: int = index // 2
            distance_to_topleft: int = 2**layer * self.__grid.cell_size
            distance_to_grid: float = index // 2 * self.__grid.cell_size * 0.5 + 0.1*self.__grid.cell_size
            x: float = self.__grid.x
            y: float = self.__grid.y
            if index % 2:
                x -= distance_to_grid
                y += distance_to_topleft
                self.__draw_row_var(var, layer, x, y)
            else:
                x += distance_to_topleft
                y -= distance_to_grid
                self.__draw_col_var(var, layer, x, y)

    def __draw_col_var(self, var_name: str, layer: int, x: float, y: float) -> None:
        """
        Draws a variable above the grid
        """
        while x < (end_x := self.__grid.get_end_x()):
            end = x + self.__grid.cell_size * 2**(layer + 1)
            if end > end_x:
                end = end_x

            self.__canvas.create_line(x, y, end, y, fill="black", width=2)

            self.__canvas.create_text(
                x + 0.5 * (end - x), y - 0.25 * self.__grid.cell_size, text=var_name, font=self.__normal_font)

            x += 2 * self.__grid.cell_size * 2**(layer + 1)

    def __draw_row_var(self, var_name: str, layer: int, x: float, y: float) -> None:
        """
        Draws a variable to the left of the grid
        """
        while y < (end_y := self.__grid.get_end_y()):
            end = y + self.__grid.cell_size * 2**(layer + 1)
            if end > end_y:
                end = end_y

            self.__canvas.create_line(x, y, x, end, fill="black", width=2)

            self.__canvas.create_text(
                x - 0.25 * self.__grid.cell_size, 
                y + 0.5 * (end - y), 
                text=var_name, font=self.__normal_font, angle=90
            )

            y += 2 * self.__grid.cell_size * 2**(layer + 1)

    def __draw_vals_and_indices(self):
        for i in range(2**self.__kvdata.get_num_vars()):
            x, y = self.__grid.grid_to_canvas_coord(*KVUtils.IndexToCoordinate(i))
            self.__canvas.create_text(
                x + 0.8*self.__grid.cell_size, y + 0.85*self.__grid.cell_size, text=str(i), font=self.__small_font)
            if len(self.__kvdata.vals.get()) > i:
                cell_center = 0.5*self.__grid.cell_size
                self.__canvas.create_text(x + cell_center, y + cell_center, text=self.__kvdata.vals.get()[i], font=self.__large_font)

    def __draw_markings(self):
        for index, marking in enumerate(self.__kvdata.markings):
            for marking_data in marking.drawables:
                line_width: int = 2
                if index == self.__kvdata.selected:
                    line_width = 4
                offset = 0.05 * self.__grid.cell_size
                x1 = self.__grid.grid_to_canvas_x(marking_data.x1) + offset
                y1 = self.__grid.grid_to_canvas_y(marking_data.y1) + offset
                x2 = self.__grid.grid_to_canvas_x(marking_data.x2) - offset
                y2 = self.__grid.grid_to_canvas_y(marking_data.y2) - offset
                openings = marking_data.openings
                col = marking.tkinter_color
                marking_lines = marking_data.marking_lines
                marking_lines.clear()
                if Edge.LEFT not in openings:
                    marking_lines.append(
                        self.__canvas.create_line(x2, y1, x2, y2, fill=col, width=line_width)
                    )
                if Edge.RIGHT not in openings:
                    marking_lines.append(
                        self.__canvas.create_line(x1, y1, x1, y2, fill=col, width=line_width)
                    )
                if Edge.TOP not in openings:
                    marking_lines.append(
                        self.__canvas.create_line(x1, y2, x2, y2, fill=col, width=line_width)
                    )
                if Edge.BOTTOM not in openings:
                    marking_lines.append(
                        self.__canvas.create_line(x1, y1, x2, y1, fill=col, width=line_width)
                    )

    def update_markingdata(self, marking: Optional[Marking] = None) -> None:
        if marking is None:
            marking = self.__kvdata.get_selected_marking()
        marking.drawables = self.indices_to_markingdata(marking.indices)

    def indices_to_markingdata(self, indices: list[int]) -> list[MarkingData]:
        ret: list[MarkingData] = []
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2), openings = self.__get_rect_bounds(block, indices)
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret

    def __get_rect_bounds(self, block: list[int], marking: list[int]) -> tuple[tuple[int, int], tuple[int, int], Edge]:
        get_tl_and_br: Callable[[tuple[int, int, int, int], tuple[int, int]], tuple[int, int, int, int]] = lambda acc, xy: (
            min(acc[0], xy[0]), min(acc[1], xy[1]), max(acc[2], xy[0]), max(acc[3], xy[1]))

        kv_max_x = self.__kvdata.dimensions[0] - 1
        kv_max_y = self.__kvdata.dimensions[1] - 1

        min_x, min_y, max_x, max_y = reduce(get_tl_and_br, [KVUtils.IndexToCoordinate(i) for i in block], (kv_max_x, kv_max_y, 0, 0))
        max_x += 1
        max_y += 1
        openings: Edge = Edge.NONE
        if min_x == 0 and KVUtils.CoordinateToIndex(kv_max_x, min_y) in marking:
            openings |= Edge.RIGHT
        if max_x == self.__kvdata.dimensions[0] and KVUtils.CoordinateToIndex(0, min_y) in marking:
            openings |= Edge.LEFT
        if (Edge.LEFT | Edge.RIGHT) in openings:
            openings = Edge.NONE

        if min_y == 0 and KVUtils.CoordinateToIndex(min_x, kv_max_y) in marking:
            openings |= Edge.BOTTOM
        if max_y == self.__kvdata.dimensions[1] and KVUtils.CoordinateToIndex(min_x, 0) in marking:
            openings |= Edge.TOP
        if (Edge.BOTTOM | Edge.TOP) in openings:
            openings &= Edge.LEFT | Edge.RIGHT

        return ((min_x, min_y), (max_x, max_y), openings)
    
    def remove_marking(self, marking: Marking) -> None:
        marking.indices.clear()
        for md in marking.drawables:
            self.__canvas.delete(*md.marking_lines)
        marking.drawables.clear()
    
    def canvas_to_kv_index(self, x: float, y: float) -> int:
        """
        Convert canvas coordinates to Karnaugh map index.
        """
        new_x: int = int((x - self.__grid.x) // self.__grid.cell_size)
        new_y: int = int((y - self.__grid.y) // self.__grid.cell_size)

        if new_x < 0 or new_x >= self.__kvdata.dimensions[0] or new_y < 0 or new_y >= self.__kvdata.dimensions[1]:
            return -1

        return KVUtils.CoordinateToIndex(new_x, new_y)