from collections import deque
from collections.abc import Callable, Iterator, MutableSequence
from itertools import cycle
from typing import Optional

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
    """A CyclicCache that cycles through the elements of a generator.
    If the generator exhausts it starts from the front again, 
    also allows to release items so they will get generated next.
    (released Items need to have been generated)

    :param generator: the generator for the elements
    :type generator: Iterator[T]
    """
    def __init__(self, generator: Iterator[T]) -> None:
        self.__generator: Iterator[T] = cycle(generator)
        self.__released_items: deque[T] = deque()
        self.__in_use_items: set[T] = set()
    
    def change_generator(self, generator: Iterator[T], start: Optional[T] = None) -> None:
        """changes the generator makes sure to start at the element "start" if
        "start" is None it starts with the first element
        else it rotates the generator until it "start" is the next element

        :param generator: the new generator
        :type generator: Iterator[T]
        :param start: which element in the generator to start
        :type start: Optional[T] = None
        :raises ValueError: if start isn't in the generator
        """
        if start is None:
            self.__generator = cycle(generator)
        else:
            items: deque[T] = deque(generator)
            for _ in range(len(items) + 1):
                if items[0] == start:
                    break
                items.rotate(-1)
            else:
                raise ValueError(f"{start} is not an element of the generator {generator}")
            self.__generator = cycle(items)
        self.__released_items.clear()
        self.__in_use_items.clear()

    def get_item(self) -> T:
        """gets the next item if it has released items it gets a released item else it
        generates a new item with the generator

        :return: the item
        :rtype: T
        """
        if self.__released_items:
            item = self.__released_items.popleft()
        else:
            item =  next(self.__generator)
        self.__in_use_items.add(item)
        return item
    
    def release_item(self, item: T):
        """Releases an item so it can get reused in the next get item 
        (only if it is not already in the current queue)
        released Items need to have been generated

        :param item: the item to release
        :type item: T
        """
        if item in self.__in_use_items:
            self.__in_use_items.remove(item)
            self.__released_items.append(item)

def ensure_count[T](sequence: MutableSequence[T], desired_count: int, factory: Callable[[int], T], deleter: Callable[[T], None] = lambda _:None):
    """Resizes a sequence to have the desired count.
    if the sequence is shorter than the desired count, it adds new elements with the factory
    (the parameter is the index of the new element)
    if the sequence is longer than the desired count, it pops the elements to remove and calls the deleter on them 

    :param sequence: the sequence to resize
    :type sequence: MutableSequence[T]
    :param desired_count: the length the sequence will get resized to (needs to be >= 0)
    :type desired_count: int
    :param factory: the factory to build new items (the parameter is the index of the new item in the sequence)
    :type factory: Callable[[int], T]
    :param deleter: the function to delete an Element (the parameter is the element to delete)
    (in case it isn't enough to just pop it)
    :type deleter: Callable[[T], None] = lambda _: None
    """
    assert(desired_count >= 0)
    count_difference = len(sequence) - desired_count
    if count_difference < 0:
        end = len(sequence)
        sequence.extend(factory(end + i) for i in range(-count_difference))
    elif count_difference > 0:
        [deleter(sequence.pop()) for _ in range(count_difference)]

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