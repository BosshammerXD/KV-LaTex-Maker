from collections.abc import Iterator
from dataclasses import dataclass
from tkinter import Canvas

import IterTools
from KV_Diagramm.KVData import Marking, Edge, EDGES, MarkingData

from .KVDrawable import KVDrawable
from .KVGrid import KVGrid

@dataclass
class _Edge_Lines:
    left: int = 0
    right: int = 0
    top: int = 0
    bottom: int = 0

    def reset(self) -> None:
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

    def delete_item(self, index: Edge) -> int:
        ret = self[index]
        self[index] = 0
        return ret

    def delete(self, canvas: Canvas) -> None:
        if self.left:
            canvas.delete(self.left)
        if self.right:
            canvas.delete(self.right)
        if self.top:
            canvas.delete(self.top)
        if self.bottom:
            canvas.delete(self.bottom)

    def __getitem__(self, index: Edge) -> int:
        match index:
            case Edge.LEFT:
                return self.left
            case Edge.RIGHT:
                return self.right
            case Edge.TOP:
                return self.top
            case Edge.BOTTOM:
                return self.bottom
            case _:
                return -1
    
    def __setitem__(self, index: Edge, value: int) -> None:
        match index:
            case Edge.LEFT:
                self.left = value
            case Edge.RIGHT:
                self.right = value
            case Edge.TOP:
                self.top = value
            case Edge.BOTTOM:
                self.bottom = value
            case _:
                pass
    
    def __iter__(self) -> Iterator[int]:
        if self.left:
            yield self.left
        if self.right:
            yield self.right
        if self.top:
            yield self.top
        if self.bottom:
            yield self.bottom

class KVMarkings(KVDrawable):
    __SLIM_WIDTH: int = 2
    __THICK_WIDTH: int = 4
    def __init__(self, canvas: Canvas) -> None:
        super().__init__(canvas)
        self.__selected: int = -1
        self.__marking_ids: list[tuple[str, list[_Edge_Lines]]] = []

    def set_color(self, tag: str, col: str) -> None:
        self._canvas.itemconfig(tag, fill=col)

    def update_selected(self, selected: int):
        if selected < 0:
            self.__selected = -1
        elif selected != self.__selected:
            assert(len(self.__marking_ids) > selected)
            if self.__selected != -1:  
                self._canvas.itemconfig(self.__marking_ids[self.__selected][0], width=self.__SLIM_WIDTH)
            self._canvas.itemconfig(self.__marking_ids[selected][0], width=self.__THICK_WIDTH)
            self.__selected = selected

    def delete_marking(self, index: int, tag: str):
        self._canvas.delete(tag)
        if index != self.__selected:
            self.__marking_ids.pop(index)
        elif self.__selected < 0:
            for edge_line in self.__marking_ids[index][1]:
                edge_line.reset()

    def new_marking(self, index: int, marking: Marking) -> None:
        self.__marking_ids.insert(index, (marking.TAG, [_Edge_Lines() for _ in range(len(marking.drawables))]))
        self.update_marking(index, marking.drawables, marking.tkinter_color)

    def update_marking(self, index: int, drawables: list[MarkingData], col: str) -> None:
        assert(len(self.__marking_ids) > index)
        tag, edge_lines = self.__marking_ids[index]
        if drawables:
            IterTools.ensure_count(edge_lines, len(drawables), lambda _: _Edge_Lines(), lambda x: x.delete(self._canvas))
        elif self.__marking_ids[index]:
            self._canvas.delete(tag)
            self.__marking_ids[index] = (tag, [])
        for markingdata, edge_line in zip(drawables, edge_lines):
            self.__set_lines(markingdata.edges, edge_line, col, tag)

    def update(self, markings: list[Marking]):
        for index, marking in enumerate(markings):
            self.update_marking(index, marking.drawables, marking.tkinter_color)


    def draw(self, kv_grid: KVGrid, markings: Iterator[Marking]) -> None:
        index: int = 0
        for marking in markings:
            if not len(marking.indices):
                continue
            self.draw_marking(kv_grid, index, marking.drawables)
            index += 1
    
    def draw_marking(self, kv_grid: KVGrid, index: int, drawables: list[MarkingData]) -> None:
        marking_offset: float = 0.05

        for i, marking_data in enumerate(drawables):
            x1, y1 = kv_grid.grid_to_canvas_coord(marking_data.x1 + marking_offset, marking_data.y1 + marking_offset)
            x2, y2 = kv_grid.grid_to_canvas_coord(marking_data.x2 - marking_offset, marking_data.y2 - marking_offset)
            edge_lines = self.__marking_ids[index][1][i]
            if edge_lines[Edge.LEFT]:
                self._canvas.coords(edge_lines[Edge.LEFT], x1, y1, x1, y2)
            if edge_lines[Edge.RIGHT]:
                self._canvas.coords(edge_lines[Edge.RIGHT], x2, y1, x2, y2)
            if edge_lines[Edge.TOP]:
                self._canvas.coords(edge_lines[Edge.TOP], x1, y1, x2, y1)
            if edge_lines[Edge.BOTTOM]:
                self._canvas.coords(edge_lines[Edge.BOTTOM], x1, y2, x2, y2)

    def __set_lines(self, edge: Edge, ids: _Edge_Lines, col: str, tag: str):
        for edge_to_check in EDGES:
            self.__set_line(edge, edge_to_check, ids, col, tag)
    
    def __set_line(self, edge: Edge, edge_to_check: Edge, ids: _Edge_Lines, col: str, tag: str):
        if edge_to_check in edge:
            if not ids[edge_to_check]:
                ids[edge_to_check] = self._canvas.create_line(0,0,0,0, width=KVMarkings.__SLIM_WIDTH, fill=col, tags=(tag,))
        elif ids[edge_to_check]:
            self._canvas.delete(ids.delete_item(edge_to_check))