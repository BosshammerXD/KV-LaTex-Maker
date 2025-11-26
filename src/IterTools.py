from collections.abc import Callable, Iterator

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
     :type iterator: Iterator[T]
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