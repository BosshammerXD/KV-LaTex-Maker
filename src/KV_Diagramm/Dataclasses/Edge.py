from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntFlag
from tkinter import Canvas

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
class Edge_Lines:
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