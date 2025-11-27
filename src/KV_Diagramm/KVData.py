from enum import IntFlag
from dataclasses import dataclass, field
from typing import Iterator

from Globals import DYNAMIC

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Shapes.KVMarkings import KVMarkings

class Edge(IntFlag):
    NONE = 0
    RIGHT = 1
    LEFT = 2
    TOP = 4
    BOTTOM = 8

    def kv_str(self) -> str:
        ret: str = ""
        if Edge.RIGHT in self and Edge.LEFT not in self:
            ret += "r"
        if Edge.LEFT in self and Edge.RIGHT not in self:
            ret += "l"
        if Edge.TOP in self and Edge.BOTTOM not in self:
            ret += "t"
        if Edge.BOTTOM in self and Edge.TOP not in self:
            ret += "b"
        return ret
EDGES: tuple[Edge, Edge, Edge, Edge] = (Edge.LEFT, Edge.RIGHT, Edge.TOP, Edge.BOTTOM)

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
    tkinter_color: str
    _TAG: str
    indices: list[int] =  field(default_factory=lambda: list[int]())
    drawables: list[MarkingData] = field(default_factory=lambda: [])
    @property
    def TAG(self) -> str:
        return self._TAG

@dataclass
class KVData:
    _kv_markings: KVMarkings
    vals: str
    vars: list[str]
    _selected: int = -1
    width: int = 0
    height: int = 0
    _markings: list[Marking] = field(default_factory=lambda: [])

    @property
    def selected(self) -> int:
        return self._selected
    @selected.setter
    def selected(self, val: int) -> None:
        self._selected = val
        self.__adjust_selected()
        self._kv_markings.update_selected(self._selected)
    @property
    def markings(self) -> Iterator[Marking]:
        return iter(self._markings)
    @property
    def len_markings(self) -> int:
        return len(self._markings)

    def add_marking(self, latex_color: str, tag: str, index: int = -1) -> None:
        marking = Marking(latex_color, DYNAMIC.Colors[latex_color], tag)
        if index < 0:
            self._markings.append(marking)
            self._kv_markings.new_marking(self.len_markings - 1, marking)
        else:
            self._markings.insert(index, marking)
            self._kv_markings.new_marking(index, marking)

    def remove_marking(self, index: int):
        marking = self._markings.pop(index)
        self._kv_markings.delete_marking(index, marking.TAG)
        self.__adjust_selected()

    def __adjust_selected(self) -> None:
        if not self._markings:
            self._selected = -1
        else:
            while self._selected < 0:
                self._selected += len(self._markings)
            while self._selected >= len(self._markings):
                self._selected -= len(self._markings)
        self._kv_markings.update_selected(self._selected)

    def get_num_vars(self) -> int:
        return len(self.vars)
    
    def get_selected_marking(self) -> Marking:
        return self._markings[self.selected]