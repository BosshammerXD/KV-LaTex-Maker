from collections.abc import Callable
from functools import partial

def __dfs(index: int, visited: dict[int, bool], indices_neighbour: dict[int, list[int]], block: list[int]) -> list[int]:
    visited[index] = True
    block.append(index)

    for i in indices_neighbour[index]:
        if not visited[i]:
            __dfs(i, visited, indices_neighbour, block)

    return block


def is_kv_neighbour(v1: int, v2: int) -> bool:
    return bin(v1 ^ v2).count("1") == 1


def find_kv_neigbours(val: int, others: list[int]) -> list[int]:
    f = partial(is_kv_neighbour, v2=val)
    return list(filter(f, others))


def find_different_bits(v1: int, v2: int) -> list[int]:
    bin1 = bin(v1)[2:]
    bin2 = bin(v2)[2:]
    if len(bin1) < len(bin2):
        bin1 = bin1.zfill(len(bin2))
    elif len(bin2) < len(bin1):
        bin2 = bin2.zfill(len(bin1))
    bin1 = bin1[::-1]
    bin2 = bin2[::-1]
    f: Callable[[int], bool] = lambda x: bin1[x] != bin2[x]
    return list(filter(f, range(min(len(bin1), len(bin2)))))


blocks: list[list[int]] = []


def is_direct_neighbour(v1: int, v2: int, n: int) -> bool:
    #find better solution (maybe not func needed?)
    x1, y1 = IndexToCoordinate(v1, n)
    x2, y2 = IndexToCoordinate(v2, n)
    return abs(x1 - x2) + abs(y1 - y2) == 1


def make_blocks(indices: list[int], num_vars: int) -> None:
    #pretty inefficient
    blocks.clear()

    visited: dict[int, bool] = {i: False for i in indices}
    coord_neighbours: dict[int, list[int]] = {i: list(
        filter(partial(is_direct_neighbour, i, n=num_vars), indices)) for i in indices}

    for index in indices:
        if visited[index]:
            continue

        block: list[int] = __dfs(index, visited, coord_neighbours, [])
        blocks.append(block)

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

def CoordinateToIndex(x: int, y: int, n: int) -> int:
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

def IndexToCoordinate(index: int, num_vars: int) -> tuple[int, int]:
    gray_x,gray_y = split_int_binary(index)
    x = inv_gray_code(gray_x)
    y = inv_gray_code(gray_y) 

    return x, y

if __name__ == "__main__":
    import random
    rand = random.Random(102937)
    for i in range(1000):
        CoordinateToIndex(rand.randint(0,31),rand.randint(0,31), 0)
        IndexToCoordinate(rand.randint(0,1023), 0)
        is_direct_neighbour(rand.randint(0,1023),rand.randint(0,1023), 10)
        is_kv_neighbour(rand.randint(0,1023),rand.randint(0,1023))
        make_blocks([0,1,2,3], 4)
        find_different_bits(rand.randint(0,1023),rand.randint(0,1023))
