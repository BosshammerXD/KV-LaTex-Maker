from collections import deque
from collections.abc import Callable, Iterator
from itertools import cycle

class IDGenerator[T]:
    """
    An IDGenerator generates ids using the provided generator.
    and stores released ids that can be reassigned.

    :param generator: the generator that generates ids (needs to be infinite)
    :type generator: Iterator[T]
    """
    def __init__(self, generator: Iterator[T]) -> None:
        self.__generator: Iterator[T] = generator
        self.__released_ids: deque[T] = deque()
        self.__distributed_ids: set[T] = set()
    
    def generate_id(self) -> T:
        """
        generates an id, if ids were released it reassigns.
        if there are no released ids it generates them with the generator
        if the generator gets exhausted it raises a StopIteration Error

        :return: the generated id
        :rtype: T
        """
        if self.__released_ids:
            item = self.__released_ids.popleft()
        else:    
            item = next(self.__generator)
        self.__distributed_ids.add(item)
        return item
    
    def release_id(self, id: T) -> None:
        """
        releases an id.
        released idds will be redistributed on the next idgeneration
        only releas ids that are no longer in use

        :param id: the id you want to release
        :type id: T
        """
        if id in self.__distributed_ids:
            self.__distributed_ids.remove(id)
            self.__released_ids.append(id)


class CyclicCache[T]:
    def __init__(self, generator: Iterator[T]) -> None:
        self.__generator: Iterator[T] = cycle(generator)
        self.__released_items: deque[T] = deque()
        self.__in_use_items: set[T] = set()
    
    def get_item(self) -> T:
        if self.__released_items:
            item = self.__released_items.popleft()
        else:
            item =  next(self.__generator)
        self.__in_use_items.add(item)
        return item
    
    def release_item(self, item: T):
        if item in self.__in_use_items:
            self.__in_use_items.remove(item)
            self.__released_items.append(item)

def ensure_count[T](current_ids: list[T], desired_count: int, factory: Callable[[int], T], deleter: Callable[[T], None]):
        count_difference = len(current_ids) - desired_count
        if count_difference < 0:
            current_ids.extend(factory(i) for i in range(-count_difference))
        elif count_difference > 0:
            [deleter(current_ids.pop()) for _ in range(count_difference)]

def take_n[T](iterator: Iterator[T], n: int) -> list[T]:
     """
     takes the first n elements of an Iterator
     if the iterator is exhausted before n elements are extracted it returns all elements until the iterator exhausts
     
     :param iterable: the Iterator that you take n elements from
     :type iterable: Iterator[T]
     :param n: how many elements you want to take
     :type n: int
     :return: a list of the taken elements (len(return)=min(len(iterator),n))
     :rtype: list[T]
     """
     assert(n >= 0)
     ret: list[T] = []
     for _ in range(n):
        try:
            ret.append(next(iterator))
        except StopIteration:
            return ret
     return ret