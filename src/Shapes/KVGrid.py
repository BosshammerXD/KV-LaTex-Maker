from .KVDrawable import KVDrawable
from tkinter import Canvas
import IterTools

class KVGrid(KVDrawable):
    def __init__(self, canvas: Canvas, num_cols: int = 1, num_rows: int = 1) -> None:
        super().__init__(canvas)
        self.__col_ids: list[int] = []
        self.__row_ids: list[int] = []
        self.update(num_cols, num_rows)
        self.__cell_size: float = -1
        self.__x_offset: float = -1
        self.__y_offset: float = -1

    @property
    def cell_size(self) -> float:
        return self.__cell_size
    
    @property
    def x_offset(self) -> float:
        return self.__x_offset
    
    @property
    def y_offset(self) -> float:
        return self.__y_offset

    def update(self, num_cols: int, num_rows: int) -> None:
        #how many vars need to fit to the left (analog to int(math.log(num_rows, 2))) (only need since thy take up half a cell)
        self.__x_offset_cells: int = num_rows.bit_length() // 2 
        #how many vars need to fit above
        self.__y_offset_cells: int = num_cols.bit_length() // 2 
        IterTools.ensure_count(self.__row_ids, num_rows - 1, self.__make_line, self._delete_item)
        IterTools.ensure_count(self.__col_ids, num_cols - 1, self.__make_line, self._delete_item)

    def draw(self, canvas_width: float, canvas_height: float) -> None:
        x_total: float = self.__x_offset_cells + len(self.__col_ids) + 2
        y_total: float = self.__y_offset_cells + len(self.__row_ids) + 2
        self.__cell_size = min(canvas_width / x_total, canvas_height / y_total)
        width: float = self.__cell_size * (len(self.__col_ids) + 1)
        height: float = self.__cell_size * (len(self.__row_ids) + 1)
        self.__x_offset = max(self.__x_offset_cells * self.__cell_size, (canvas_width - width) / 2)
        self.__y_offset = max(self.__y_offset_cells * self.__cell_size, (canvas_height - height) / 2)
        x_max = self.__x_offset + width
        y_max = self.__y_offset + height

        for index, col_id in enumerate(self.__col_ids):
            x = self.__x_offset + self.__cell_size * (index + 1)
            self._canvas.coords(col_id,x , self.__y_offset, x, y_max)
        for index, row_id in enumerate(self.__row_ids):
            y = self.__y_offset + self.__cell_size * (index + 1)
            self._canvas.coords(row_id, self.__x_offset, y, x_max, y)

    def __make_line(self, i: int = 0) -> int:
        return self._canvas.create_line(0,0,0,0)
    
    def grid_to_canvas_coord(self, x: float, y: float) -> tuple[float, float]:
        return x * self.__cell_size + self.__x_offset, y * self.cell_size + self.__y_offset