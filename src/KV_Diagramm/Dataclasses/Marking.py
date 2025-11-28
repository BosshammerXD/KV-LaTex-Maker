from dataclasses import dataclass, field
from Globals import DYNAMIC

from .Edge import Edge

@dataclass
class MarkingData:
    x1: float
    y1: float
    x2: float
    y2: float
    edges: Edge


@dataclass
class Marking:
    latex_color: str
    _TAG: str
    indices: list[int] =  field(default_factory=lambda: list[int]())
    drawables: list[MarkingData] = field(default_factory=lambda: [])
    @property
    def TAG(self) -> str:
        return self._TAG
    
    @property
    def tkinter_color(self) -> str:
        return DYNAMIC.Colors[self.latex_color]