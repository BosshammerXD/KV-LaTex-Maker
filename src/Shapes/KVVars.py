from dataclasses import dataclass
from functools import partial
from Globals.STATIC import FONTS
from tkinter import Canvas

import tkinter.font as tkfont

from .KVDrawableFromGrid import KVDrawableFromGrid
from .KVGrid import KVGrid

@dataclass
class _KVVar:
    lines: list[int]
    texts: list[int]

#TODO: make algorithm smarter by
#      - only changing the vars that need to be changed when the line stays same but vals differ
#      - in case of more vals make the old ones longer instead of elting everything and regenerating it again
#      - in case of less vals only delete the ones that need to be deleted and modify the new highest one so the bar length fits

class KVVars(KVDrawableFromGrid):
    def __init__(self, canvas: Canvas, vars: list[str] = []) -> None:
        super().__init__(canvas)
        self.__font = tkfont.Font(family=FONTS.TYPE, size=12)
        self.__vars = []
        self.__var_ids = []
        self.update(vars)

    def update(self, vars: list[str]) -> None:
        if vars == self.__vars:
            return
        self.__vars = vars.copy()
        for kv_var in self.__var_ids:
            self._canvas.delete(*kv_var.lines)
            self._canvas.delete(*kv_var.texts)
        kv_var_func = partial(self.__make_KVVar, num_elems=len(vars))
        self.__var_ids: list[_KVVar] = [kv_var_func(index, var) for index, var in enumerate(vars)]

    def draw(self, kv_grid: KVGrid) -> None:
        cell_size = kv_grid.cell_size
        self.__font.configure(size=int(cell_size//4))
        num_left_vars: int = len(self.__var_ids) // 2
        num_top_vars: int = len(self.__var_ids) - num_left_vars

        for index, kv_var in enumerate(self.__var_ids):
            max_layer = (num_left_vars if index % 2 else num_top_vars) - 1
            self.__draw_var(kv_var, cell_size, (kv_grid.x_offset, kv_grid.y_offset), index, max_layer)
    
    def __draw_var(self, kv_var: _KVVar, cell_size: float, tl_grid: tuple[float, float], index: int, max_layer: int) -> None:
        is_row: bool = bool(index % 2)
        layer = index // 2
        line_length: float = 2**(layer + 1) * cell_size
        start: float = tl_grid[1 if is_row else 0] + line_length / 2
        depth: float = tl_grid[0 if is_row else 1] - layer * cell_size / 2
        text_offset = 0.25 * cell_size
        offset_from_grid = 0.1 * cell_size
        for i in range(len(kv_var.lines)):
            v1 = start + 2 * i * line_length
            v2 = v1 + line_length
            if layer == max_layer:
                v2 -= line_length / 2
            if is_row:
                self._canvas.coords(kv_var.lines[i], depth - offset_from_grid, v1, depth - offset_from_grid, v2)
                self._canvas.coords(kv_var.texts[i], depth - text_offset, (v1 + v2) / 2)
            else:
                self._canvas.coords(kv_var.lines[i], v1, depth - offset_from_grid, v2, depth - offset_from_grid)
                self._canvas.coords(kv_var.texts[i], (v1 + v2) / 2, depth - text_offset)

    def __make_KVVar(self, index: int, var: str, num_elems: int) -> _KVVar:
        angle = 90 if index % 2 else 0
        if index % 2:
            num_elems //= 2
            index //= 2
        else:
            num_elems -= num_elems // 2
            index -= index // 2
        num_objs: int = 2**(num_elems - index - 1)
        if num_objs > 1:
            num_objs //= 2
        return _KVVar(
                [self._canvas.create_line(0,0,0,0, width=2) for _ in range(num_objs)],
                [self._canvas.create_text(0,0, text=var, angle=angle, font=self.__font) for _ in range(num_objs)]
            )