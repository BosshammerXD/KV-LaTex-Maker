from __future__ import annotations
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Callable, Optional
from DataStructures.CompleteTree import CompleteTree
from Globals.STATIC import FONTS
from tkinter import Canvas

import tkinter.font as tkfont

from .KVDrawable import KVDrawable
from .KVGrid import KVGrid

@dataclass
class _LineTextPair:
    line_id: int
    text_id: int

    def delete(self, canvas: Canvas):
        canvas.delete(self.line_id, self.text_id)
    
    def __iter__(self) -> Iterator[int]:
        yield self.line_id
        yield self.text_id

@dataclass
class _KVVarIDs:
    _val: Optional[_LineTextPair] = None
    _tree: CompleteTree[_LineTextPair] = field(default_factory=lambda:CompleteTree())

    @property
    def val(self) -> Optional[_LineTextPair]:
        return self._val

    @property
    def num_vars(self) -> int:
        if self._val is None:
            return 0
        else:
            return self._tree.height + 1

    def add_var(self, factory: Callable[[],_LineTextPair]):
        if self._val is None:
            self._val = factory()
        else:
            self._tree.add_layer(factory)
    
    def remove_var(self, canvas: Canvas) -> None:
        if self._val is None:
            return
        if self._tree.height != 0:
            self._tree.remove_layer(lambda x: x.delete(canvas))
        else:
            self._val.delete(canvas)
            self._val = None
    
    def resize(self, new_vars: Iterable[str], factory: Callable[[str],_LineTextPair], canvas: Canvas) -> None:
        new_vars_iter = iter(new_vars)
        try:
            first = next(new_vars_iter)
            if self._val is None:
                self._val = factory(first)
            vars = list(new_vars_iter)
            if not vars:
                self._tree.clear()
            else:
                self._tree.resize(len(vars), lambda i: factory(vars[i]), lambda x: x.delete(canvas))
        except StopIteration:
            self._val = None
    
    def __iter__(self) -> Iterator[list[_LineTextPair]]:
        return reversed(self._tree.get_layers())
    
    def delete(self, canvas: Canvas):
        while self._val is not None:
            self.remove_var(canvas)

#TODO: make algorithm smarter by
#      - only changing the vars that need to be changed when the line stays same but vals differ
#      - in case of more vals make the old ones longer instead of elting everything and regenerating it again
#      - in case of less vals only delete the ones that need to be deleted and modify the new highest one so the bar length fits

class KVVars(KVDrawable):
    def __init__(self, canvas: Canvas) -> None:
        super().__init__(canvas)
        self.__font = tkfont.Font(family=FONTS.TYPE, size=12)
        self.__vars: list[str] = []
        self.__top_var_ids: _KVVarIDs = _KVVarIDs()
        self.__left_var_ids: _KVVarIDs = _KVVarIDs()

    def update(self, vars: list[str]) -> None:
        if vars == self.__vars:
            return
        self.__vars = vars.copy()
        top_vars = vars[::2]
        left_vars = vars[1::2]
        self.__top_var_ids.resize(reversed(top_vars), self.__make_LineTextID(False), self._canvas)
        self.__left_var_ids.resize(reversed(left_vars), self.__make_LineTextID(True), self._canvas)

    def draw(self, kv_grid: KVGrid) -> None:
        cell_size = kv_grid.cell_size
        self.__font.configure(size=int(cell_size//4))

        for index, layer in enumerate(self.__top_var_ids):
            self.__draw_layer(layer, index, cell_size, (kv_grid.x_offset, kv_grid.y_offset), False, False)
        if (val := self.__top_var_ids.val) is not None:
            self.__draw_layer([val], self.__top_var_ids.num_vars - 1, cell_size, (kv_grid.x_offset, kv_grid.y_offset), False, True)
        for index, layer in enumerate(self.__left_var_ids):
            self.__draw_layer(layer, index, cell_size, (kv_grid.x_offset, kv_grid.y_offset), True, False)
        if (val := self.__left_var_ids.val) is not None:
            self.__draw_layer([val], self.__left_var_ids.num_vars - 1, cell_size, (kv_grid.x_offset, kv_grid.y_offset), True, True)

    def __draw_layer(self, layer: list[_LineTextPair], index: int, cell_size: float, tl_grid: tuple[float, float], is_left: bool, is_root: bool) -> None:
        line_length: float = 2**(index + 1) * cell_size
        start: float = tl_grid[1 if is_left else 0] + line_length / 2
        depth: float = tl_grid[0 if is_left else 1] - index * cell_size / 2
        text_offset = 0.25 * cell_size
        offset_from_grid = 0.1 * cell_size
        for i, (line, text) in enumerate(layer):
            v1 = start + 2 * i * line_length
            v2 = v1 + line_length
            if is_root:
                v2 -= line_length / 2
            if is_left:
                self._canvas.coords(line, depth - offset_from_grid, v1, depth - offset_from_grid, v2)
                self._canvas.coords(text, depth - text_offset, (v1 + v2) / 2)
            else:
                self._canvas.coords(line, v1, depth - offset_from_grid, v2, depth - offset_from_grid)
                self._canvas.coords(text, (v1 + v2) / 2, depth - text_offset)
    
    def __make_LineTextID(self, is_left: bool) -> Callable[[str], _LineTextPair]:
        angle = 90 if is_left else 0
        def ret_func(var: str):
            return _LineTextPair(
                self._canvas.create_line(0,0,0,0, width=2),
                self._canvas.create_text(0,0, text=var, angle=angle, font=self.__font)
            )
        return ret_func

    def __len__(self) -> int:
        return len(self.__vars)