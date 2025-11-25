from collections.abc import Iterator
from dataclasses import dataclass
from tkinter import Canvas

import IterTools
from KV_Diagramm.KVData import Marking, Edge, EDGES

from .KVDrawable import KVDrawable
from .KVGrid import KVGrid

@dataclass
class _Edge_Lines:
    left: int = 0
    right: int = 0
    top: int = 0
    bottom: int = 0

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
        self.__marking_ids: list[list[_Edge_Lines]] = []

    def update_selected(self, selected: int):
        assert(selected >= 0)
        assert(len(self.__marking_ids) > selected)
        if self.__selected != -1:  
            self.__set_width(self.__selected, self.__SLIM_WIDTH)
        self.__set_width(selected, self.__THICK_WIDTH)
        self.__selected = selected
    
    def __set_width(self, index: int, linewidth: int):
        for edge_line in self.__marking_ids[index]:
            for edge in edge_line:
                self._canvas.itemconfig(edge, width=linewidth)

    def update_marking(self, index: int, marking: Marking) -> None:
        assert(len(self.__marking_ids) >= index)
        if len(self.__marking_ids) == index:
            self.__marking_ids.append([_Edge_Lines() for _ in range(len(marking.drawables))])
        IterTools.ensure_count(self.__marking_ids[index], len(marking.drawables), lambda _: _Edge_Lines(), lambda x: x.delete(self._canvas))
        col = marking.tkinter_color
        for i, markingdata in enumerate(marking.drawables):
            self.__set_lines(markingdata.edges, self.__marking_ids[index][i], col, markingdata.tag)
        print(self.__marking_ids[index])

    def update(self, markings: list[Marking]):
        for index, marking in enumerate(markings):
            self.update_marking(index, marking)


    def draw(self, kv_grid: KVGrid, markings: list[Marking]) -> None:
        for index, marking in enumerate(markings):
            self.draw_marking(kv_grid, marking, index)
    
    def draw_marking(self, kv_grid: KVGrid, marking: Marking, index: int) -> None:
        marking_offset: float = 0.05

        for i, marking_data in enumerate(marking.drawables):
            x1, y1 = kv_grid.grid_to_canvas_coord(marking_data.x1 + marking_offset, marking_data.y1 + marking_offset)
            x2, y2 = kv_grid.grid_to_canvas_coord(marking_data.x2 - marking_offset, marking_data.y2 - marking_offset)
            edge_lines = self.__marking_ids[index][i]
            print(x1,y1,x2,y2,edge_lines)
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