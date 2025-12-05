from collections import deque
from collections.abc import Callable, Iterable, Iterator

class CompleteListBinTree[T]:
    """a Binary Tree that is always complete and realised with a list
    the layers are inverse to their height (so the root is on layer height - 1 the children of the root are on layer height - 2 and the leafes are on layer 0)
    it is optimized to:
    - add a new root and then completing the tree again by generating new nodes with the factory; O(n*factory())
    - remove a root and delete it alongside the right subtree of th root using the deleter; O(n/2) + O(deleter(n/2))
    - get the tree elements layer by layer; O(2n)
    - get the height of the tree; O(1)
    - get a specific layer; O(2h) (where h is the number of elements in the layer)

    :param factory: a factory function that generates an element (the parameter is the height of the element)
    :type factory: Callable[[int], T]
    :param deleter: a function that deletes mutiple elements at once (the parameters are two Iterable of the elements to delete)
    the first parameter has the removedd roots, the second the reomved subtrees
    :type deleter: Callable[[Iterable[T], Iterable[T]], None] = lambda _: None
    """
    def __init__(self, factory: Callable[[int], T], deleter: Callable[[Iterable[T], Iterable[T]], None] = lambda i1, i2: None) -> None:
        self.__height: int = 0
        self._factory = factory
        self._deleter = deleter
        self._nodes: deque[T] = deque()

    @property
    def height(self) -> int:
        return self.__height
    
    def add_layers(self, num_layers: int = 1, *new_roots: T) -> None:
        assert(num_layers > 0)
        assert(len(new_roots) <= num_layers)
        for i in range(self.__height, self.__height + num_layers):
            
            self._nodes.appendleft(new_roots[i - self.__height] if i - self.__height < len(new_roots) else self._factory(i))
            self._nodes.extend(self._factory(height) for height in self.__get_heights(i - 1))
        self.__height += num_layers
    
    def add_layer(self, new_root: T) -> None:
        self._nodes.appendleft(new_root)
        self._nodes.extend(self._factory(height) for height in self.__get_heights(self.__height - 1))
        self.__height += 1

    def remove_layers(self, num_layers: int = 1) -> None:
        assert(num_layers > 0)
        if len(self._nodes) < num_layers:
            raise StopIteration("tried to remove more layers than the tree has")
        roots_to_delete: list[T] = []
        subtrees_to_delete: list[T] = []
        for _ in range(num_layers):
            roots_to_delete.append(self._nodes.popleft())
            subtrees_to_delete.extend(self._nodes.pop() for _ in range(len(self._nodes) // 2, len(self._nodes)))
        self._deleter(roots_to_delete, subtrees_to_delete)
        self.__height -= num_layers
    
    def resize(self, desired_layer_count: int, *new_roots: T) -> None:
        difference = self.__height - desired_layer_count
        if difference < 0:
            self.add_layers(-difference, *new_roots)
        elif difference > 0:
            self.remove_layers(difference)
    
    def clear(self) -> None:
        roots_to_delete: list[T] = [self._nodes.popleft() for _ in range(self.__height)]
        subtrees_to_delete = self._nodes
        self._nodes = deque()
        self._deleter(roots_to_delete, subtrees_to_delete)

    def get_tree_layers(self) -> Iterator[list[T]]:
        if not self._nodes:
            return
        index_queue: deque[int] = deque((0,))
        holder: list[T] = []
        temp: int = 1
        while index_queue:
            index = index_queue.popleft()
            holder.append(self._nodes[index])
            index_queue.extend(i for i in self.__get_children(index, temp.bit_length()))
            if len(holder) == temp:
                yield holder
                holder = []
                temp <<= 1
    
    def get_tree_layer(self, layer: int) -> Iterator[T]:
        offset = self.__child_offset(self.__height - layer)
        index = layer
        yield self._nodes[index]
        temp: list[int] = []
        for i in range(layer):
            temp = temp + [i] + temp
        for i in temp:
            index += offset + i
            yield self._nodes[index]

    @staticmethod
    def __child_offset(child_layer: int) -> int:
        return 2**(child_layer + 1) - 1

    def __get_children(self, node_index: int, layer: int) -> Iterator[int]:
        assert(node_index >= 0)
        if layer == self.height:
            return
        yield node_index + 1
        yield node_index + 1 + self.__child_offset(self.__height - layer - 1)

    @staticmethod
    def __get_heights(height: int) -> Iterator[int]:
        if height < 0:
            return
        stack = [height]
        while stack:
            current = stack.pop()
            yield current
            if current > 0:
                stack.append(current - 1)
                stack.append(current - 1)