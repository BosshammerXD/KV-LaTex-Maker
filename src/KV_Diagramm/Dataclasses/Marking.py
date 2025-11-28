from dataclasses import dataclass, field
from Globals import DYNAMIC

from .Edge import Edge
from KV_Diagramm import KVUtils

@dataclass
class MarkingData:
    x1: float
    y1: float
    x2: float
    y2: float
    edges: Edge

    @staticmethod
    def from_indices(indices: list[int], width: int, height: int) -> list[MarkingData]:
        idx_set: set[int] = set(indices)
        ret: list[MarkingData] = []
        kv_max_x = width - 1
        kv_max_y = height - 1
        for block in KVUtils.make_blocks(indices):
            (x1,y1), (x2,y2) = MarkingData.__get_rect_bounds(block)
            openings: Edge = Edge.NONE
            if not(x1 == 0 and KVUtils.CoordinateToIndex(kv_max_x, y1) in idx_set):
                openings |= Edge.LEFT
            if not(x2 == width and KVUtils.CoordinateToIndex(0, y1) in idx_set):
                openings |= Edge.RIGHT
            if Edge.LEFT not in openings and Edge.RIGHT not in openings:
                openings |= Edge.RIGHT | Edge.LEFT

            if not(y1 == 0 and KVUtils.CoordinateToIndex(x1, kv_max_y) in idx_set):
                openings |= Edge.TOP
            if not(y2 == height and KVUtils.CoordinateToIndex(x1, 0) in idx_set):
                openings |= Edge.BOTTOM
            if Edge.TOP not in openings and Edge.BOTTOM not in openings:
                openings |= Edge.TOP | Edge.BOTTOM
            
            ret.append(MarkingData(x1,y1,x2,y2,openings))
        return ret
    
    @staticmethod
    def __get_rect_bounds(block: list[tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
        xs, ys = zip(*block)
        min_x, max_x = min(xs), max(xs) + 1
        min_y, max_y = min(ys), max(ys) + 1

        return ((min_x, min_y), (max_x, max_y))


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