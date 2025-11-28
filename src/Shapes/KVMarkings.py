from tkinter import Canvas

import IterTools
from KV_Diagramm.Dataclasses.Marking import Marking
from KV_Diagramm.Dataclasses.Edge import Edge, EDGES, Edge_Lines

from .KVDrawable import KVDrawable
from .KVGrid import KVGrid

class KVMarkings(KVDrawable):
    __SLIM_WIDTH: int = 2
    __THICK_WIDTH: int = 4
    def __init__(self, canvas: Canvas) -> None:
        super().__init__(canvas)
        self.__marking_ids: dict[str, list[Edge_Lines]] = {}
        self.__selected_tag: str = ""

    def set_color(self, tag: str, col: str) -> None:
        self._canvas.itemconfig(tag, fill=col)

    def update_selected(self, selected: Marking):
        if self.__selected_tag:
            self._canvas.itemconfig(self.__selected_tag, width=self.__SLIM_WIDTH)
        self.__selected_tag = selected .TAG
        self._canvas.itemconfig(selected.TAG, width=self.__THICK_WIDTH)

    def delete_marking(self, tag: str):
        self._canvas.delete(tag)
        if tag == self.__selected_tag:
            for edge_line in self.__marking_ids[tag]:
                edge_line.reset()
        else:
            self.__marking_ids.pop(tag)

    def new_marking(self, marking: Marking) -> None:
        self.__marking_ids[marking.TAG] = [Edge_Lines() for _ in range(len(marking.drawables))]
        self.update_marking(marking)

    def update_marking(self, marking: Marking) -> None:
        assert(marking.TAG in self.__marking_ids)
        edge_lines = self.__marking_ids[marking.TAG]
        if marking.drawables:
            IterTools.ensure_count(edge_lines, len(marking.drawables), lambda _: Edge_Lines(), lambda x: x.delete(self._canvas))
        elif self.__marking_ids[marking.TAG]:
            self._canvas.delete(marking.TAG)
            self.__marking_ids[marking.TAG] = []
        for markingdata, edge_line in zip(marking.drawables, edge_lines):
            self.__set_lines(markingdata.edges, edge_line, marking.tkinter_color, marking.TAG, marking.TAG == self.__selected_tag)
    
    def draw_marking(self, kv_grid: KVGrid, marking: Marking) -> None:
        marking_offset: float = 0.05

        for i, marking_data in enumerate(marking.drawables):
            x1, y1 = kv_grid.grid_to_canvas_coord(marking_data.x1 + marking_offset, marking_data.y1 + marking_offset)
            x2, y2 = kv_grid.grid_to_canvas_coord(marking_data.x2 - marking_offset, marking_data.y2 - marking_offset)
            edge_lines = self.__marking_ids[marking.TAG][i]
            if edge_lines[Edge.LEFT]:
                self._canvas.coords(edge_lines[Edge.LEFT], x1, y1, x1, y2)
            if edge_lines[Edge.RIGHT]:
                self._canvas.coords(edge_lines[Edge.RIGHT], x2, y1, x2, y2)
            if edge_lines[Edge.TOP]:
                self._canvas.coords(edge_lines[Edge.TOP], x1, y1, x2, y1)
            if edge_lines[Edge.BOTTOM]:
                self._canvas.coords(edge_lines[Edge.BOTTOM], x1, y2, x2, y2)

    def __set_lines(self, edge: Edge, ids: Edge_Lines, col: str, tag: str, is_selected: bool):
        line_width = self.__THICK_WIDTH if is_selected else self.__SLIM_WIDTH
        for edge_to_check in EDGES:
            self.__set_line(edge, edge_to_check, ids, col, tag, line_width)
    
    def __set_line(self, edge: Edge, edge_to_check: Edge, ids: Edge_Lines, col: str, tag: str, line_width: int):
        if edge_to_check in edge:
            if not ids[edge_to_check]:
                ids[edge_to_check] = self._canvas.create_line(0,0,0,0, width=line_width, fill=col, tags=(tag,))
        elif ids[edge_to_check]:
            self._canvas.delete(ids.delete_item(edge_to_check))