from __future__ import annotations
from collections.abc import Callable
from DataStructures.KVVarIDs import KVVarIDs, LineTextPair
from GeneralDataTypes.IDiedString import IDiedString
from Globals.STATIC import FONTS
from tkinter import Canvas

import tkinter.font as tkfont

from .KVDrawable import KVDrawable
from .KVGrid import KVGrid

class _LayerLayout:
    def __init__(self, layer_index: int, kv_grid: KVGrid, is_left: bool) -> None:
        depth = (kv_grid.x_offset if is_left else kv_grid.y_offset) - layer_index * kv_grid.cell_size / 2
        self.line_length: int = 2**(layer_index + 1) * kv_grid.cell_size
        self.grid_start: float = (kv_grid.y_offset if is_left else kv_grid.x_offset) + self.line_length / 2
        self.grid_offset: float = depth - 0.1 * kv_grid.cell_size
        self.text_offset: float = depth - 0.25 * kv_grid.cell_size

class _Line:
    def __init__(self, segment_index: int, layout: _LayerLayout) -> None:
        self.layout: _LayerLayout = layout
        self.start: float = layout.grid_start + 2 * segment_index * layout.line_length
        self.end: float = self.start + layout.line_length
    
    @property
    def middle(self) -> float:
        return (self.start + self.end) / 2

class KVVars(KVDrawable):
    __VAR_TEXT_TAG: str = "KVVar"

    def __init__(self, canvas: Canvas) -> None:
        super().__init__(canvas)
        self.__font = tkfont.Font(family=FONTS.TYPE, size=12)
        self.__vars: list[str | IDiedString] = []
        self.__top_var_ids: KVVarIDs = KVVarIDs(self.__make_LineTextID_from_index(False), canvas)
        self.__left_var_ids: KVVarIDs = KVVarIDs(self.__make_LineTextID_from_index(True), canvas)

    def update(self, vars: list[str]) -> None:
        if vars == self.__vars:
            return
        if len(vars) > len(self.__vars):
            self.__vars.extend(vars[len(self.__vars)::])
        elif len(vars) < len(self.__vars):
            [e.__del__() for _ in range(len(self.__vars) - len(vars)) if isinstance(e := self.__vars.pop(), IDiedString)]
        [self.__update_tree_layer(v_o, v_n) for (v_n, v_o) in zip(vars, self.__vars) if v_n != v_o]
        num_left_vars: int = len(vars) // 2
        num_top_vars: int = len(vars) - num_left_vars
        self.__top_var_ids.resize(num_top_vars)
        self.__left_var_ids.resize(num_left_vars)


    def __update_tree_layer(self, old_val: IDiedString | str, new_val: str) -> None:
        if isinstance(old_val, str): return
        old_val.val = new_val
        self._canvas.itemconfig(f"{KVVars.__VAR_TEXT_TAG}{old_val.id}", text=new_val)


    def draw(self, kv_grid: KVGrid) -> None:
        cell_size = kv_grid.cell_size
        self.__font.configure(size=int(cell_size//4))
        self.__draw_layers(kv_grid, False)
        self.__draw_layers(kv_grid, True)

    def __move_left_text_line(self, line_id: int, text_id: int, coords: _Line) -> None:
        self._canvas.coords(line_id, coords.layout.grid_offset, coords.start, coords.layout.grid_offset, coords.end)
        self._canvas.coords(text_id, coords.layout.text_offset, coords.middle)
    
    def __move_top_text_line(self, line_id: int, text_id: int, coords: _Line) -> None:
        self._canvas.coords(line_id, coords.start, coords.layout.grid_offset, coords.end, coords.layout.grid_offset)
        self._canvas.coords(text_id, coords.middle, coords.layout.text_offset)

    def __draw_layers(self, kv_grid: KVGrid, is_left: bool):
        layers = self.__left_var_ids if is_left else self.__top_var_ids
        move_func = self.__move_left_text_line if is_left else self.__move_top_text_line
        for index, layer in enumerate(layers):
            layout = _LayerLayout(index, kv_grid, is_left)
            [move_func(line_id, text_id, _Line(i, layout)) for i, (line_id, text_id) in enumerate(layer)]
        if layers.val is not None:
            layout = _LayerLayout(layers.num_vars - 1, kv_grid, is_left)
            coords = _Line(0, layout)
            coords.end -= layout.line_length / 2
            move_func(layers.val.line_id, layers.val.text_id, coords)

    def __make_LineTextID_from_index(self, is_left: bool) -> Callable[[int], LineTextPair]:
        angle = 90 if is_left else 0
        def ret_func(index: int):
            string = self.__vars[int(is_left) + 2 * index]
            if isinstance(string, str):
                text = IDiedString(string)
                self.__vars[int(is_left) + 2 * index] = text
            else:
                text = string
            return LineTextPair(
                self._canvas.create_line(0,0,0,0, width=2),
                self._canvas.create_text(0,0, text=text.val, angle=angle, font=self.__font, tags=(f"{KVVars.__VAR_TEXT_TAG}{text.id}",)),
                text.id
            )
        return ret_func