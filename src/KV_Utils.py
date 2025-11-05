from collections.abc import Callable
from functools import partial
import math

class KV_Utils:
    KARNAUGH_TEMPLATE: str = """
\\karnaughmap{{{num_vars}}}{{{title}}}%
{{{my_vars}}}
{{{vals}}}
{{{ovals}}}
"""

    OVAL_TEMPLATE: str = """\\put({x},{y}){{\\oval({delta_x},{delta_y}){side}}}"""

    def __init__(self, colors: list[str]):
        self.colors = colors
        
    @staticmethod
    def color_item(item: str, color: str) -> str:
        return "\\textcolor{{{color}}}{{%\n{item}}}".format(color=color, item=item)

    @classmethod
    def __dfs(cls, index: int, visited: dict[int, bool], indices_neighbour: dict[int, list[int]], block: list[int]) -> list[int]:
        visited[index] = True
        block.append(index)

        for i in indices_neighbour[index]:
            if not visited[i]:
                cls.__dfs(i, visited, indices_neighbour, block)

        return block

    @staticmethod
    def is_kv_neighbour(v1: int, v2: int) -> bool:
        return bin(v1 ^ v2).count("1") == 1
    
    @classmethod
    def find_kv_neigbours(cls, val: int, others: list[int]) -> list[int]:
        f = partial(cls.is_kv_neighbour, v2=val)
        return list(filter(f, others))
    
    @staticmethod
    def find_different_bits(v1: int, v2: int) -> list[int]:
        bin1 = bin(v1)[2:]
        bin2 = bin(v2) [2:]
        if len(bin1) < len(bin2):
            bin1 = bin1.zfill(len(bin2))
        elif len(bin2) < len(bin1):
            bin2 = bin2.zfill(len(bin1))
        bin1 = bin1[::-1]
        bin2 = bin2[::-1]
        f: Callable[[int], bool] = lambda x: bin1[x] != bin2[x]
        return list(filter(f, range(min(len(bin1), len(bin2)))))
    
    blocks: list[list[int]] = []

    @classmethod
    def is_direct_neighbour(cls, v1: int, v2: int, n: int) -> bool:
        x1, y1 = cls.IndexToCoordinate(v1, n)
        x2, y2 = cls.IndexToCoordinate(v2, n)
        return abs(x1 - x2) + abs(y1 - y2) == 1

    @classmethod
    def make_blocks(cls, indices: list[int], n: int) -> None:
        cls.blocks.clear()

        visited: dict[int, bool] = {i: False for i in indices}
        coord_neighbours: dict[int, list[int]] = {i: list(filter(partial(cls.is_direct_neighbour, i, n=n), indices)) for i in indices}

        for index in indices:
            if visited[index]:
                continue

            block: list[int] = cls.__dfs(index, visited, coord_neighbours, [])
            cls.blocks.append(block)

    @staticmethod
    def CoordinateToIndex(x: int, y: int, n: int) -> int:
        num_cols = 2**math.ceil(n/2)
        num_rows = 2**math.floor(n/2)
        col_bits: str = ""
        row_bits: str = ""

        mid = num_cols // 2
        last = 0

        while mid:
            if (x < mid if last else x >= mid):
                col_bits += "1"
                last ^= 1
            else:
                col_bits += "0"
            
            if x >= mid:
                x -= mid

            mid //= 2
        
        col_bits = col_bits.zfill(math.ceil(n/2))

        mid = num_rows // 2
        last = 0
        
        while mid:
            if (y < mid if last else y >= mid):
                row_bits += "1"
                last ^= 1
            else:
                row_bits += "0"

            if y >= mid:
                y -= mid

            mid //= 2
        row_bits = row_bits.zfill(math.floor(n/2))

        #TODO: optimize if possible
        binary = ""
        for i in range(1, len(col_bits) + 1):
            binary = (row_bits[-i] if i < len(row_bits) + 1 else "") + col_bits[-i] + binary

        return int(binary, 2)

    @staticmethod 
    def IndexToCoordinate(index: int, n: int) -> tuple[int, int]:
        if n < 1:
            raise ValueError("Number of variables must be at least 1")
        elif index < 0 or index >= 2**n:
            raise ValueError(f"Index out of bounds. index: {index}, n: {n}")
        elif n == 1:
            return (0, index - 1)

        # Convert the index to binary
        binary: str = bin(index)[2:].zfill(n)[::-1]

        col_bits: str = "".join(binary[i] for i in range(0, n, 2)).zfill(math.ceil(n/2))[::-1]
        row_bits: str = "".join(binary[i] for i in range(1, n, 2)).zfill(math.floor(n/2))[::-1]

        possible_x: list[int] = list(range(2**math.ceil(n/2)))
        possible_y: list[int] = list(range(2**math.floor(n/2)))
        
        last: int = 0
        for c in col_bits:
            v = int(c)
            if v ^last == 1:
                possible_x = possible_x[len(possible_x)//2:]
            else:
                possible_x = possible_x[:len(possible_x)//2]

            last ^= v

        last: int = 0
        for c in row_bits:
            v = int(c)
            if v ^ last == 1:
                possible_y = possible_y[len(possible_y)//2:]
            else:
                possible_y = possible_y[:len(possible_y)//2]

            last ^= v
        
        if len(possible_x) == 0 or len(possible_y) == 0:
            raise ValueError("No possible coordinates found")
        elif len(possible_x) != 1 or len(possible_y) != 1:
            raise ValueError("More than one possible coordinate found")
        
        return possible_x[0], possible_y[0]
