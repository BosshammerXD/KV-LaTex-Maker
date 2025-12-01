from KV_Diagramm import KVUtils
from Globals.STATIC import FONTS
from tkinter import Canvas

from .KVDrawableFromGrid import KVDrawableFromGrid
from .KVGrid import KVGrid

import IterTools
import tkinter.font as tkfont

class KVIndices(KVDrawableFromGrid):
    def __init__(self, canvas: Canvas) -> None:
        super().__init__(canvas)
        self.__font = tkfont.Font(family=FONTS.TYPE)
        self.__index_ids: list[int] = []
    
    def update(self, num_indices: int):
        if num_indices == len(self.__index_ids):
            return
        def factory(i: int) -> int:
            return self.__make_text(str(i))
        IterTools.ensure_count(self.__index_ids, num_indices, factory, self._delete_item)
    
    def draw(self, kv_grid: KVGrid) -> None:
        self.__font.configure(size=int(kv_grid.cell_size // 6))
        low_in_cell_x: float = 0.8 * kv_grid.cell_size
        low_in_cell_y: float = 0.85 * kv_grid.cell_size
        for index, id in enumerate(self.__index_ids):
            x,y = kv_grid.grid_to_canvas_coord(*KVUtils.IndexToCoordinate(index))
            self._canvas.coords(id, x + low_in_cell_x, y + low_in_cell_y)
    
    def __make_text(self, text: str) -> int:
        return self._canvas.create_text(0,0,text=text, font=self.__font)