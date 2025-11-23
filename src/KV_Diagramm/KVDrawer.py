from dataclasses import dataclass
from tkinter import Canvas, Event
from typing import Optional

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
    
    def update_size(self, cell_size: float, grid_width: int, grid_height: int, canv_width: int, canv_height: int):
        self.cell_size = cell_size
        self.width = self.cell_size * grid_width
        self.height = self.cell_size * grid_height
        self.x = (canv_width - self.width) / 2
        self.y = (canv_height - self.height) / 2
        self.marking_offset = 0.05 * self.cell_size


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
        self.__width = self.__canvas.winfo_width()
        self.__height = self.__canvas.winfo_height()
        if self.__kvdata.get_num_vars() == 0:
            return
        
        num_left_vars = self.__kvdata.get_num_vars() // 2
        num_top_vars = self.__kvdata.get_num_vars() - num_left_vars

        self.__kvdata.width = 2**num_top_vars
        self.__kvdata.height = 2**num_left_vars

        cell_width = self.__width / (self.__kvdata.width + num_top_vars)
        cell_height = self.__height / (self.__kvdata.height + num_left_vars)

        self.__grid.update_size(
            min(cell_width, cell_height), 
            self.__kvdata.width, self.__kvdata.height,
            self.__width, self.__height
        )

        self.__large_font = (FONTS.TYPE, int(self.__grid.cell_size // 2))
        self.__normal_font = (FONTS.TYPE, int(self.__grid.cell_size // 4))
        self.__small_font = (FONTS.TYPE, int(self.__grid.cell_size // 6))

        self.draw()

    def draw(self) -> None:
        self.__canvas.delete("all")
        if self.__kvdata.get_num_vars() == 0:
            return
        self.__draw_vars()
        self.__draw_grid()
        self.__draw_indices()
        self.__draw_vals()
        for marking in self.__kvdata.markings:
            line_width = 4 if marking is self.__kvdata.get_selected_marking() else 2
            col = marking.tkinter_color
            for marking_data in marking.drawables:
                self.__canvas.delete(*marking_data.marking_lines)
                self.draw_marking_lines(marking_data, col, line_width)

    def __draw_grid(self) -> None:
        """
        Draw lines on the canvas.
        """
        for c in range(1, self.__kvdata.width):
            x = self.__grid.grid_to_canvas_x(c)
            self.__canvas.create_line(x, self.__grid.y, x, self.__grid.y + self.__grid.height)
        for r in range(1, self.__kvdata.height):
            y = self.__grid.grid_to_canvas_y(r)
            self.__canvas.create_line(self.__grid.x, y, self.__grid.x + self.__grid.width, y)

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
            is_row: bool = bool(index % 2)
            if is_row:
                x -= distance_to_grid
                y += distance_to_topleft
            else:
                x += distance_to_topleft
                y -= distance_to_grid
            self.__draw_var(var, layer, x, y, is_row)

    def __draw_var(self, var_name: str, layer: int, x: float, y: float, is_row: bool) -> None:
        def float_range(start: float, stop: float, step: float):
            while start < stop:
                yield start
                start += step
        
        end_moving = self.__grid.get_end_y() if is_row else self.__grid.get_end_x()
        moving = y if is_row else x
        #offset from the grid/last var
        offset = (x if is_row else y) - 0.25*self.__grid.cell_size
        for i in float_range(moving, end_moving, self.__grid.cell_size * 2**(layer + 2)):
            end = i + self.__grid.cell_size * 2**(layer + 1)
            if end > end_moving:
                end = end_moving
            middle_of_line = 0.5 * (i + end)
            if is_row:
                self.__canvas.create_line(x, i, x, end, fill="black", width=2)
                self.__canvas.create_text(
                    offset,
                    middle_of_line,
                    text=var_name, font=self.__normal_font, angle=90
                )
            else:
                self.__canvas.create_line(i, y, end, y, fill="black", width=2)
                self.__canvas.create_text(
                    middle_of_line,
                    offset,
                    text=var_name, font=self.__normal_font, angle=0
                )

    def __draw_vals(self):
        cell_center = 0.5*self.__grid.cell_size
        for index, char in enumerate(self.__kvdata.vals.get()):
            x,y = self.__grid.grid_to_canvas_coord(*KVUtils.IndexToCoordinate(index))
            self.__canvas.create_text(x + cell_center, y + cell_center, text=char, font=self.__large_font)
    
    def __draw_indices(self):
        low_in_cell_x: float = 0.8 * self.__grid.cell_size
        low_in_cell_y: float = 0.85 * self.__grid.cell_size
        for i in range(2**self.__kvdata.get_num_vars()):
            x, y = self.__grid.grid_to_canvas_coord(*KVUtils.IndexToCoordinate(i))
            self.__canvas.create_text(
                x + low_in_cell_x, y + low_in_cell_y, text=str(i), font=self.__small_font)

    def draw_marking_lines(self, marking_data: MarkingData, col: str, line_width: int):
        marking_data.marking_lines.clear()
        x1 = self.__grid.grid_to_canvas_x(marking_data.x1) + self.__grid.marking_offset
        y1 = self.__grid.grid_to_canvas_y(marking_data.y1) + self.__grid.marking_offset
        x2 = self.__grid.grid_to_canvas_x(marking_data.x2) - self.__grid.marking_offset
        y2 = self.__grid.grid_to_canvas_y(marking_data.y2) - self.__grid.marking_offset
        openings = marking_data.edges
        marking_lines = marking_data.marking_lines

        if Edge.LEFT in openings:
            marking_lines.append(
                self.__canvas.create_line(x1, y1, x1, y2, fill=col, width=line_width)
            )
        if Edge.RIGHT in openings:
            marking_lines.append(
                self.__canvas.create_line(x2, y1, x2, y2, fill=col, width=line_width)
            )
        if Edge.TOP in openings:
            marking_lines.append(
                self.__canvas.create_line(x1, y1, x2, y1, fill=col, width=line_width)
            )
        if Edge.BOTTOM in openings:
            marking_lines.append(
                self.__canvas.create_line(x1, y2, x2, y2, fill=col, width=line_width)
            )

    def update_markingdata(self, marking: Optional[Marking] = None, is_selected: bool = True) -> None:
        if marking is None:
            marking = self.__kvdata.get_selected_marking()
        for marking_data in marking.drawables:
            self.__canvas.delete(*marking_data.marking_lines)
        marking.drawables = self.indices_to_markingdata(marking.indices)
        line_width = 4 if is_selected else 2
        for marking_data in marking.drawables:
            self.draw_marking_lines(marking_data, marking.tkinter_color, line_width)

    def indices_to_markingdata(self, indices: list[int]) -> list[MarkingData]:
        ret: list[MarkingData] = []
        kv_max_x = self.__kvdata.width - 1
        kv_max_y = self.__kvdata.height - 1
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2) = self.__get_rect_bounds(block)
            openings: Edge = Edge.RIGHT | Edge.LEFT | Edge.TOP | Edge.BOTTOM
            if x1 == 0 and KVUtils.CoordinateToIndex(kv_max_x, y1) in indices:
                openings &= ~Edge.LEFT
            if x2 == self.__kvdata.width and KVUtils.CoordinateToIndex(0, y1) in indices:
                openings &= ~Edge.RIGHT

            if y1 == 0 and KVUtils.CoordinateToIndex(x1, kv_max_y) in indices:
                openings &= ~Edge.TOP
            if y2 == self.__kvdata.height and KVUtils.CoordinateToIndex(x1, 0) in indices:
                openings &= ~Edge.BOTTOM
            
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret

    def __get_rect_bounds(self, block: list[int]) -> tuple[tuple[int, int], tuple[int, int]]:
        coords = [KVUtils.IndexToCoordinate(i) for i in block]
        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        max_x += 1
        max_y += 1

        return ((min_x, min_y), (max_x, max_y))
    
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

        if new_x < 0 or new_x >= self.__kvdata.width or new_y < 0 or new_y >= self.__kvdata.height:
            return -1

        return KVUtils.CoordinateToIndex(new_x, new_y)