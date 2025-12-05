from collections import deque
from collections.abc import Iterator
from functools import partial
from typing import Optional
from IterTools import take_n


def is_kv_neighbour(v1: int, v2: int) -> bool:
    return (v1 ^ v2).bit_count() == 1


def find_kv_neigbours(val: int, others: list[int]) -> Iterator[int]:
    return filter(partial(is_kv_neighbour, v2=val), others)

def find_different_bits(v1: int, v2: int) -> Iterator[int]:
    differences = v1 ^ v2
    index = 0
    while differences:
        if differences & 1:
            yield index
        index += 1
        differences >>= 1

def get_different_bit(index: int, others: list[int]) -> Optional[int]:
    if len(neighbourlist := take_n(find_kv_neigbours(index, others), 1)) == 0:
        return None
    ret: int = index ^ neighbourlist[0]
    assert(ret.bit_count() == 1)
    return ret.bit_length() - 1

def make_blocks(indices: list[int]) -> list[list[tuple[int, int]]]:
    #modified Flood Fill Algorithm
    coords: set[tuple[int, int]] = {IndexToCoordinate(i) for i in indices}
    islands: list[list[tuple[int, int]]] = []
    while coords:
        item: tuple[int, int] = coords.pop()
        queue: deque[tuple[int, int]] = deque([item])
        island: list[tuple[int, int]] = []
        while queue:
            p: tuple[int, int] = queue.popleft()
            island.append(p)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbour: tuple[int, int] = (p[0] + dx, p[1] + dy)
                if neighbour in coords:
                    coords.remove(neighbour)
                    queue.append(neighbour)
        islands.append(island)
    return islands

def expand_block(indices: list[int], bit: int) -> None:
    indices.extend([i ^ (1 << bit) for i in indices])

def shrink_block(indices: list[int], index: int) -> None:
    def compare_bit(v1: int, v2: int, bit_offset: int) -> bool:
        return bool(1 & ((v1 ^ v2) >> bit_offset)) 
    mid = len(indices) // 2
    relative_index: int
    index_in_current: int = indices.index(index)
    if index_in_current < mid:
        relative_index = next(find_kv_neigbours(index, indices[mid:]))
    else:
        relative_index = next(find_kv_neigbours(index, indices[:mid]))
    change = next(find_different_bits(index, relative_index))

    indices[:mid] = list(filter(lambda x: not compare_bit(x, relative_index, change), indices))
    indices[mid:] = []

def get_rect_bounds_from_block(block: list[int]) -> tuple[tuple[int, int], tuple[int, int]]:
        coords = [IndexToCoordinate(i) for i in block]
        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs) + 1
        min_y, max_y = min(ys), max(ys) + 1

        return ((min_x, min_y), (max_x, max_y))

def join_ints_binary(value1: int, value2: int) -> int:
    """interweaves two binary values be reading over them bit for bit and extending another value by their bits
    value1 will generate the 0,2,4,.. bit of the retval
    value2 will generate the 1,3,5,... bit of the retval
    if one value is shorter than the other the shorter value gets extended with zeros"""
    ret: int = 0
    acc: int = 0
    while value1 or value2:
        ret |= (value1 & 1) << acc
        value1 >>= 1
        acc += 1
        ret |= (value2 & 1) << acc
        value2 >>= 1
        acc += 1
    return ret 

def to_gray_code(value: int) -> int:
    return value ^ (value >> 1)

def CoordinateToIndex(x: int, y: int) -> int:
    gray_x = to_gray_code(x)
    gray_y = to_gray_code(y)
    return join_ints_binary(gray_x, gray_y)

def split_int_binary(value: int) -> tuple[int, int]:
    """takes a Binary Value and splits it into two values
    the first value has the 0,2,4,... bit (even ones)
    the second value has the 1,3,5,... bit (odd ones)"""
    x,y = value & 1,(value & 2) >> 1
    acc: int = 0
    value >>= 2
    while value:
        y |= (value & 2) << acc
        acc += 1
        x |= (value & 1) << acc
        value >>= 2
    return x,y

def inv_gray_code(value: int) -> int:
    """inverts gray code
    inv_gray_code(gray_code(num))=num"""
    ret: int = value
    while value:
        value >>= 1
        ret ^= value
    return ret

def IndexToCoordinate(index: int) -> tuple[int, int]:
    gray_x,gray_y = split_int_binary(index)
    x = inv_gray_code(gray_x)
    y = inv_gray_code(gray_y) 

    return x, y