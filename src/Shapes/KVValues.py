from tkinter import Canvas

from KV_Diagramm import KVUtils
from Globals.STATIC import FONTS
import IterTools

import tkinter.font as tkfont

from .KVGrid import KVGrid
from .KVDrawableFromGrid import KVDrawableFromGrid

class KVValues(KVDrawableFromGrid):
    def __init__(self, canvas: Canvas, new_values: str = "") -> None:
        super().__init__(canvas)
        self.__font = tkfont.Font(family=FONTS.TYPE, size=12)
        self.__values: str = ""
        self.__val_ids: list[int] = []
        self.update(new_values)
    
    def update(self, new_values: str) -> None:
        if new_values == self.__values:
            return
        self.__resize_val_ids(new_values)
        self.__update_text_contents(new_values)
        self.__values = new_values
    
    def __resize_val_ids(self, new_values: str) -> None:
        def factory(i: int) -> int:
            return self.__make_text(new_values[len(self.__values) + i])
        IterTools.ensure_count(self.__val_ids, len(new_values), factory, self._delete_item)
    
    def __update_text_contents(self, new_values: str) -> None:
        def update_text_at_index(index: int) -> None:
            self._canvas.itemconfig(self.__val_ids[index], text=new_values[index])
        smallest_len = min(len(new_values), len(self.__values))
        [update_text_at_index(i) for i in range(smallest_len) if new_values[i] != self.__values[i]]

    def draw(self, kv_grid: KVGrid):
        self.__font.configure(size=int(kv_grid.cell_size // 2))
        cell_center = 0.5*kv_grid.cell_size
        for index, id in enumerate(self.__val_ids):
            x,y = kv_grid.grid_to_canvas_coord(*KVUtils.IndexToCoordinate(index))
            self._canvas.coords(id, x + cell_center, y + cell_center)
    
    def __make_text(self, value: str) -> int:
        return self._canvas.create_text(0,0, text=value, font=self.__font)
