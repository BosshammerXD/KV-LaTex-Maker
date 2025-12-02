from collections.abc import Callable
from typing import Optional


class CompleteTree[T]:
    def __init__(self):
        self.__nodes: list[T] = []
        self.__height: int = 0
    
    @property
    def height(self) -> int:
        return self.__height

    def add_layer(self, factory: Callable[[], T]) -> None:
        nodes_len = len(self.__nodes)
        self.__nodes.extend(factory() for _ in range(nodes_len + 1))
        self.__height += 1
    
    def remove_layer(self, deleter: Optional[Callable[[T], None]] = None) -> None:
        if not self.__nodes:
            return
        start = len(self.__nodes) // 2
        if deleter is not None:
            [deleter(node) for node in self.__nodes[start:]]
        self.__nodes[start:] = []
        self.__height -= 1
    
    def get_layers(self) -> list[list[T]]:
        temp: int = 1
        ret: list[list[T]] = []
        holder: list[T] = []
        for node in self.__nodes:
            holder.append(node)
            if len(holder) == temp:
                ret.append(holder)
                holder = []
                temp <<= 1
        return ret
    
    def resize(self, desired_count: int, factory: Callable[[int], T], deleter: Optional[Callable[[T], None]] = None) -> None:
        assert(desired_count >= 0)
        difference = self.height - desired_count
        if difference < 0:
            current_height = self.height
            [self.add_layer(lambda:factory(i + current_height)) for i in range(-difference)]
        elif difference > 0:
            start = 2**desired_count - 1
            if deleter is not None:
                [deleter(node) for node in self.__nodes[start:]]
            self.__nodes[start:] = []
            self.__height -= difference
    
    def clear(self, deleter: Optional[Callable[[T], None]] = None) -> None:
        if self.__height == 0:
            return
        if deleter is not None:
            [deleter(node) for node in self.__nodes]
        self.__nodes = []
        self.__height = 0