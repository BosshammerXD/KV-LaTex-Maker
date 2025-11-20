from tkinter import StringVar
from dataclasses import dataclass, field


@dataclass
class MarkingData:
    x1: float
    y1: float
    x2: float
    y2: float
    openings: str
    marking_lines: list[int] = field(default_factory=lambda: [])


@dataclass
class Marking:
    indices: list[int]
    drawables: list[MarkingData]
    latex_color: str
    tkinter_color: str


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
