from collections import deque
from collections.abc import Iterator
from functools import partial


def is_kv_neighbour(v1: int, v2: int) -> bool:
    return bin(v1 ^ v2).count("1") == 1


def find_kv_neigbours(val: int, others: list[int]) -> Iterator[int]:
    f = partial(is_kv_neighbour, v2=val)
    return filter(f, others)


def find_different_bits(v1: int, v2: int) -> list[int]:
    differences = v1 ^ v2
    index = 0
    indices: list[int] = []
    while differences:
        if differences & 1:
            indices.append(index)
        index += 1
        differences >>= 1
    return indices


def make_blocks(indices: list[int]) -> list[list[int]]:
    #modified Flood Fill Algorithm
    coord_to_indices: dict[tuple[int, int], int] = {IndexToCoordinate(i) : i for i in indices} 
    islands: list[list[int]] = []
    while coord_to_indices:
        item: tuple[tuple[int, int], int] = coord_to_indices.popitem()
        island: list[int] = [item[1]]
        queue: deque[tuple[int, int]] = deque([item[0]])
        while queue:
            p: tuple[int, int] = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbour: tuple[int, int] = (p[0] + dx, p[1] + dy)
                if neighbour in coord_to_indices:
                    queue.append(neighbour)
                    island.append(coord_to_indices.pop(neighbour))
        islands.append(island)
    return islands

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

if __name__ == "__main__":
    import random
    rand = random.Random(102937)
    for i in range(1000):
        CoordinateToIndex(rand.randint(0,31),rand.randint(0,31))
        IndexToCoordinate(rand.randint(0,1023))
        is_kv_neighbour(rand.randint(0,1023),rand.randint(0,1023))
        make_blocks([0,1,2,3])
        find_different_bits(rand.randint(0,1023),rand.randint(0,1023))
