from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from itertools import chain
from tkinter import Canvas

from DataStructures.CompleteListBinTree import CompleteListBinTree


@dataclass
class LineTextPair:
    line_id: int
    text_id: int
    str_id: int
    
    def __iter__(self) -> Iterator[int]:
        yield self.line_id
        yield self.text_id

class KVVarIDs:
    def __init__(self, factory: Callable[[int], LineTextPair], canvas: Canvas) -> None:
        self.__factory = factory
        self.__deleter = self.__get_deleter(canvas)
        self.__tree: CompleteListBinTree[LineTextPair] = CompleteListBinTree(factory, self.__deleter)
        self.__val: LineTextPair | None = None

    def __get_deleter(self, canvas: Canvas) -> Callable[[Iterable[LineTextPair], Iterable[LineTextPair]], None]:
        return lambda popped_roots, popped_subtrees: canvas.delete(*chain(*popped_roots), *chain(*popped_subtrees))

    @property
    def val(self) -> LineTextPair | None:
        return self.__val

    @property
    def num_vars(self) -> int:
        return 0 if self.__val is None else self.__tree.height + 1
    
    def resize(self, num_vars: int) -> None:
        assert(num_vars >= 0)
        if num_vars == 0:
            return self.clear()
        current_vars = self.num_vars

        if num_vars > current_vars and self.__val is not None:
            self.__tree.resize(num_vars - 1, self.__val)
        else:
            self.__tree.resize(num_vars - 1)
        
        if num_vars > current_vars:
            self.__val = self.__factory(num_vars - 1) #indices start from 0 but len is 1
        elif num_vars < current_vars and self.__val is not None:
            self.__deleter([self.__val], [])
            #technically this data doesn't need to get generated, but could be reused from tree
            #but that would make the code less clean so I decided to regenrate it
            self.__val = self.__factory(num_vars - 1)
    
    def clear(self) -> None:
        if self.__val is not None:
            self.__deleter([self.__val], [])
            self.__val = None
        self.__tree.resize(0)

    def __iter__(self) -> Iterator[list[LineTextPair]]:
        return reversed(list(self.__tree.get_tree_layers()))