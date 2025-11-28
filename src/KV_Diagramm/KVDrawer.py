from collections.abc import Iterable
from enum import IntFlag, Enum
from tkinter import Canvas

from KV_Diagramm.Dataclasses.KVData import KVData

from .Dataclasses.Marking import Marking
from Shapes.KVIndices import KVIndices
from Shapes.KVGrid import KVGrid
from Shapes.KVMarkings import KVMarkings
from Shapes.KVValues import KVValues
from Shapes.KVVars import KVVars

class KVFlags(IntFlag):
    NONE = 0
    GRID = 1
    VARS = 2
    VALS = 4
    IDXS = 8
    ALL = 15

class GridUpdateMode(Enum):
    NONE = 0
    UPDATE = 1
    NEW_DIM_UPDATE = 2

class KVDrawer:
    def __init__(self, canvas: Canvas, kv_markings: KVMarkings) -> None:
        self.__canvas: Canvas = canvas
        self.__kv_grid: KVGrid = KVGrid(canvas)
        self.__kv_vars: KVVars = KVVars(canvas)
        self.__kv_values: KVValues = KVValues(canvas)
        self.__kv_indices: KVIndices = KVIndices(canvas)
        self.__kv_markings: KVMarkings = kv_markings
        self.draw_flags: KVFlags = KVFlags.NONE
        self.__width: int = canvas.winfo_width()
        self.__height: int = canvas.winfo_height()
        self.__resize_id: str = ""
    
    def draw(self, markings: Iterable[Marking] = ()) -> None:
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
    
    def update(self, kv_data: KVData, new_vars: list[str] = [], new_values: str = "", changed_markings: list[Marking] = [], draw_grid: GridUpdateMode = GridUpdateMode.NONE) -> None:
        if new_vars:
            self.__kv_vars.update(new_vars)
            self.draw_flags |= KVFlags.VARS
        if draw_grid == GridUpdateMode.NEW_DIM_UPDATE:
            self.__width = self.__canvas.winfo_width()
            self.__height = self.__canvas.winfo_height()
        if draw_grid:
            self.__kv_grid.update(kv_data.width, kv_data.height)
            self.__kv_indices.update(2**kv_data.get_num_vars())
            self.draw_flags |= KVFlags.ALL
        if new_values:
            self.__kv_values.update(new_values)
            self.draw_flags |= KVFlags.VALS
        if changed_markings:
            [self.__kv_markings.update_marking(m) for m in changed_markings]
            self.draw(changed_markings)
        else:
            self.draw(kv_data.markings if draw_grid else [])
    
    def set_marking_color(self, marking_tag: str, color: str) -> None:
        self.__kv_markings.set_color(marking_tag, color)
    
    def delete_marking(self, marking_tag: str) -> None:
        self.__kv_markings.delete_marking(marking_tag)
    
    def schedule_resize(self, kv_data: KVData) -> None:
        if self.__resize_id:
            self.__canvas.after_cancel(self.__resize_id)
        self.__resize_id = self.__canvas.after(100, lambda:self.update(kv_data, draw_grid=GridUpdateMode.NEW_DIM_UPDATE))

    def canvas_to_grid_coord(self, canvas_x: int, canvas_y: int) -> tuple[int, int]:
        new_x: int = int((canvas_x - self.__kv_grid.x_offset) // self.__kv_grid.cell_size)
        new_y: int = int((canvas_y - self.__kv_grid.y_offset) // self.__kv_grid.cell_size)
        return new_x, new_y