from enum import IntFlag
from tkinter import StringVar
from dataclasses import dataclass, field

class Edge(IntFlag):
    NONE = 0
    RIGHT = 1
    LEFT = 2
    TOP = 4
    BOTTOM = 8

    def __str__(self) -> str:
        ret: str = ""
        if Edge.RIGHT in self:
            ret += "r"
        if Edge.LEFT in self:
            ret += "l"
        if Edge.TOP in self:
            ret += "t"
        if Edge.BOTTOM in self:
            ret += "b"
        return ret

@dataclass
class MarkingData:
    x1: float
    y1: float
    x2: float
    y2: float
    openings: Edge
    marking_lines: list[int] = field(default_factory=lambda: [])


@dataclass
class Marking:
    latex_color: str
    tkinter_color: str
    indices: list[int] =  field(default_factory=lambda: list[int]())
    drawables: list[MarkingData] = field(default_factory=lambda: [])


@dataclass
class KVData:
    title: StringVar
    vals: StringVar
    selected: int = -1
    dimensions: tuple[int, int] = (0, 0)
    vars: list[str] = field(default_factory=lambda: [])
    markings: list[Marking] = field(default_factory=lambda: [])

    def get_num_vars(self) -> int:
        return len(self.vars)
    
    def get_selected_marking(self) -> Marking:
        return self.markings[self.selected]