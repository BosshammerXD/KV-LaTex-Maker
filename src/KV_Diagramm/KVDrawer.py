from tkinter import Canvas, Event

from Shapes.KVGrid import KVGrid
from Shapes.KVValues import KVValues
from Shapes.KVVars import KVVars
from Shapes.KVIndices import KVIndices
from Shapes.KVMarkings import KVMarkings

from .KVData import Edge, KVData, Marking, MarkingData
from . import KVUtils

class KVDrawer:
    def __init__(self, canvas: Canvas, kvdata: KVData) -> None:
        self.__canvas = canvas
        self.__kvdata = kvdata
        self.grid: KVGrid = KVGrid(canvas)
        self.kv_vars: KVVars = KVVars(canvas)
        self.kv_values: KVValues = KVValues(canvas)
        self.kv_indices: KVIndices = KVIndices(canvas)
        self.kv_markings: KVMarkings = KVMarkings(canvas)
        self.__last_resize_id: str = ""
    #
    #
    #
    #region Events
    def on_resize(self, event: Event) -> None: #type: ignore[no-untyped-def]
        """
        Handle window resize event.
        """
        if self.__last_resize_id == "":
            self.__last_resize_id = self.__canvas.after(10, self.update_sizes)

    def update_sizes(self) -> None:
        """
        Update the sizes of the cells based on the current canvas size.
        """
        self.__last_resize_id = ""
        self.__width = self.__canvas.winfo_width()
        self.__height = self.__canvas.winfo_height()
        if self.__kvdata.get_num_vars() == 0:
            return
        
        num_left_vars = self.__kvdata.get_num_vars() // 2
        num_top_vars = self.__kvdata.get_num_vars() - num_left_vars

        self.__kvdata.width = 2**num_top_vars
        self.__kvdata.height = 2**num_left_vars

        self.kv_vars.update(self.__kvdata.vars)
        self.grid.update(self.__kvdata.width, self.__kvdata.height)
        self.kv_values.update(self.__kvdata.vals)
        self.kv_indices.update(2**self.__kvdata.get_num_vars())
        self.draw_all()
    #endregion
    #
    #
    #
    #region Drawing
    #TODO: if above not pratical only redraw, when movement is done to reduce lagspikes
    def draw_all(self) -> None:
        if self.__kvdata.get_num_vars() == 0:
            return
        self.grid.draw(self.__width, self.__height)
        self.kv_vars.draw(self.grid)
        self.kv_values.draw(self.grid)
        self.kv_indices.draw(self.grid)
        self.kv_markings.draw(self.grid, self.__kvdata.markings)
    #endregion
    #
    #
    #
    #region Interfacing methods
    def update_markingdata(self, marking: Marking, index: int) -> None:
        marking.drawables = self.indices_to_markingdata(marking.indices)
        self.kv_markings.update_marking(self.__kvdata.selected, marking)
        self.kv_markings.update_selected(self.__kvdata.selected)
        self.kv_markings.draw_marking(self.grid, index, marking)

    def indices_to_markingdata(self, indices: list[int]) -> list[MarkingData]:
        ret: list[MarkingData] = []
        kv_max_x = self.__kvdata.width - 1
        kv_max_y = self.__kvdata.height - 1
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2) = self.__get_rect_bounds(block)
            openings: Edge = Edge.NONE
            if not(x1 == 0 and KVUtils.CoordinateToIndex(kv_max_x, y1) in indices):
                openings |= Edge.LEFT
            if not(x2 == self.__kvdata.width and KVUtils.CoordinateToIndex(0, y1) in indices):
                openings |= Edge.RIGHT
            if Edge.LEFT not in openings and Edge.RIGHT not in openings:
                openings |= Edge.RIGHT | Edge.LEFT

            if not(y1 == 0 and KVUtils.CoordinateToIndex(x1, kv_max_y) in indices):
                openings |= Edge.TOP
            if not(y2 == self.__kvdata.height and KVUtils.CoordinateToIndex(x1, 0) in indices):
                openings |= Edge.BOTTOM
            if Edge.TOP not in openings and Edge.BOTTOM not in openings:
                openings |= Edge.TOP | Edge.BOTTOM
            
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret
    #endregion
    #
    #
    #
    #region Utility methods
    def __get_rect_bounds(self, block: list[int]) -> tuple[tuple[int, int], tuple[int, int]]:
        coords = [KVUtils.IndexToCoordinate(i) for i in block]
        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs) + 1
        min_y, max_y = min(ys), max(ys) + 1

        return ((min_x, min_y), (max_x, max_y))
    
    def canvas_to_kv_index(self, x: float, y: float) -> int:
        """
        Convert canvas coordinates to Karnaugh map index.
        """
        new_x: int = int((x - self.grid.x_offset) // self.grid.cell_size)
        new_y: int = int((y - self.grid.y_offset) // self.grid.cell_size)

        if new_x < 0 or new_x >= self.__kvdata.width or new_y < 0 or new_y >= self.__kvdata.height:
            return -1

        return KVUtils.CoordinateToIndex(new_x, new_y)
    #endregion