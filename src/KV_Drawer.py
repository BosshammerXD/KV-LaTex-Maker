from collections.abc import Callable
from functools import reduce
from tkinter import Canvas, Event, StringVar
import math
from KV_Utils import KV_Utils
from Globals import DYNAMIC
from Globals.STATIC import FONTS, DEF_KV_VALUES

class KV_Drawer:
    """
    Class to draw Karnaugh maps using Tkinter.
    """
    col_map: dict[str, str] = DYNAMIC.Colors

    def __init__(self, my_canvas: Canvas) -> None:
        self.my_canvas = my_canvas
    
        self.my_canvas.bind("<Button-1>", self.on_click) #type: ignore[no-untyped-call]
        self.my_canvas.bind("<Button-3>", self.on_right_click) #type: ignore[no-untyped-call]
        self.my_canvas.bind("<Configure>", self.on_resize) #type: ignore[no-untyped-call]

        self.__vars: list[str] = []
        self.dimensions: tuple[int, int] = (0, 0)
        self.vals: StringVar = StringVar(value=DEF_KV_VALUES.VALUES)
        self.vals.trace_add("write", lambda x,y,z: self.draw())  # Update on change
        self.title: StringVar = StringVar(value=DEF_KV_VALUES.TITLE)

        self.__width: int = my_canvas.winfo_width()
        self.__height: int = my_canvas.winfo_height()
        self.__cell_size: float = 0

        self.__grid_width: float = 0
        self.__grid_height: float = 0
        self.__start_x: float = 0
        self.__start_y: float = 0

        self.__col_index: int = 0
        self.__current_indices: list[int] = []
        self.current_col: StringVar = StringVar(value="red")
        self.__marking_index: int = 0
        self.current_col.trace_add("write", lambda *args: self.draw()) #type: ignore[no-untyped-call]
        self.__markings : list[tuple[StringVar|str, list[int]]] = [(self.current_col, self.__current_indices)]

    #region: Properties
    @property
    def my_vars(self) -> list[str]:
        """
        Get the variables for the Karnaugh map.
        """
        return self.__vars.copy()
    
    @my_vars.setter
    def my_vars(self, my_vars: list[str]) -> None:
        """
        Set the variables for the Karnaugh map.
        """
        self.__vars = my_vars.copy()
        self.dimensions = (2**math.ceil(len(my_vars) / 2), 2**math.floor(len(my_vars) / 2))
        self.update_sizes()
    #endregion: Properties
    #
    #
    #
    #region: Events
    def on_click(self, event: Event) -> None: #type: ignore[no-untyped-def]
        """
        Handle left mouse button click event.
        """

        x= self.canvas_to_kv_index(event.x, event.y)
        if x == -1:
            print("Invalid click")
            return

        if len(self.__current_indices) == 0:
            self.__current_indices.append(x)
            self.draw()
            return

        neighbours = KV_Utils.find_kv_neigbours(x, self.__current_indices)
        if len(neighbours) == 0:
            print("No neighbours")
            return
        different_bits = KV_Utils.find_different_bits(x, neighbours[0])
        if len(different_bits) != 1:
            print("Not a neighbour")
            return

        new_vals = [x]

        for val in self.__current_indices:
            if val == neighbours[0]:
                continue
            val = val ^ (1 << different_bits[0])
            new_vals.append(val)
            
        self.__current_indices.extend(new_vals)
        self.draw()

    
    def on_right_click(self, event: Event) -> None: #type: ignore[no-untyped-def]
        """
        Handle right mouse button click event.
        """
        x = self.canvas_to_kv_index(event.x, event.y)

        if x not in self.__current_indices:
            print("Invalid click")
            return

        if len(self.__current_indices) == 1:
            self.__current_indices.clear()
            self.draw()
            return
        
        index_in_current = self.__current_indices.index(x)

        mid = len(self.__current_indices) // 2
        relative_index: int
        if index_in_current < mid: 
            relative_index = KV_Utils.find_kv_neigbours(x, self.__current_indices[mid:])[0]
            change = KV_Utils.find_different_bits(x, relative_index)[0]

            val = relative_index & (1 << change)	

            self.__current_indices[mid:] = list(filter(lambda x: x & (1 << change) == val, self.__current_indices))
            self.__current_indices[:mid] = []
        else:
            relative_index = KV_Utils.find_kv_neigbours(x, self.__current_indices[:mid])[0]
            change = KV_Utils.find_different_bits(x, relative_index)[0]

            val = relative_index & (1 << change)

            self.__current_indices[:mid] = list(filter(lambda x: x & (1 << change) == val, self.__current_indices))
            self.__current_indices[mid:] = []
        self.draw()

    def on_resize(self, event: Event) -> None: #type: ignore[no-untyped-def]
        """
        Handle window resize event.
        """
        self.__width = int(self.my_canvas.winfo_width())
        self.__height = int(self.my_canvas.winfo_height())
        if len(self.__vars) == 0:
            return
        self.update_sizes()
        self.draw()
    #endregion: Events
    #
    #
    #
    #region: Drawing
    def draw(self) -> None:
        self.my_canvas.delete("all")
        if len(self.__vars) == 0:
            return
        # Grid lines
        self.__draw_lines()

        for i in range(2**len(self.__vars)):
            x,y = KV_Utils.IndexToCoordinate(i, len(self.__vars))
            x *= self.__cell_size
            y *= self.__cell_size
            x += self.__start_x
            y += self.__start_y
            self.my_canvas.create_text(x + 0.8*self.__cell_size,y + 0.85*self.__cell_size, text=str(i), font=self.__small_font)
            if len(self.vals.get()) > i:
                self.my_canvas.create_text(x + 0.5*self.__cell_size,y + 0.5*self.__cell_size, text=self.vals.get()[i], font=self.__large_font)
        
        for i in range(len(self.__vars)):
            self.__draw_line(self.__vars[i], i)
        
        for col, indices in self.__markings:
            KV_Utils.make_blocks(indices, len(self.__vars))
            line_width: int = 2
            if isinstance(col, StringVar):
                col = col.get()
                line_width = 4
            col = self.col_map[col]

            for block in KV_Utils.blocks:
                (x1, y1), (x2, y2), openings = self.__get_rect_bounds(block, indices)
                x1 = x1 * self.__cell_size + self.__start_x
                y1 = y1 * self.__cell_size + self.__start_y
                x2 = x2 * self.__cell_size + self.__start_x
                y2 = y2 * self.__cell_size + self.__start_y
                self.__draw_rect(x1,y1,x2 + self.__cell_size, y2 + self.__cell_size, col, openings, line_width)

        
    
    def __draw_lines(self) -> None:
        """
        Draw lines on the canvas.
        """
        for c in range(1, self.dimensions[0]):
            x = self.__start_x + c * self.__cell_size
            self.my_canvas.create_line(x, self.__start_y, x, self.__start_y + self.__grid_height)
        for r in range(1, self.dimensions[1]):
            y = self.__start_y + r * self.__cell_size
            self.my_canvas.create_line(self.__start_x, y, self.__start_x + self.__grid_width, y)
        
    
    def __draw_line(self, var_name: str, order: int) -> None:
        magnitude: int = (order // 2)
        distance_to_topleft: int = 2**magnitude * self.__cell_size
        x: float
        y: float
        end: float
        if order % 2 == 0:
            x = distance_to_topleft + self.__start_x
            y = self.__start_y - order // 2 * self.__cell_size * 0.5 - 0.1*self.__cell_size
            while x < self.__start_x + self.__grid_width:
                end = x + self.__cell_size * 2**(magnitude + 1)
                if end > self.__start_x + self.__grid_width:
                    end = self.__start_x + self.__grid_width

                self.my_canvas.create_line(x, y, end, y, fill="black", width=2)

                self.my_canvas.create_text(x + 0.5 * (end - x), y - 0.25 * self.__cell_size, text=var_name, font=self.__normal_font)

                x += 2 * self.__cell_size * 2**(magnitude + 1)  
        else:
            x = self.__start_x - order // 2 * self.__cell_size * 0.5 - 0.1*self.__cell_size
            y = distance_to_topleft + self.__start_y
            while y < self.__start_y + self.__grid_height:
                end = y + self.__cell_size * 2**(magnitude + 1)
                if end > self.__start_y + self.__grid_height:
                    end = self.__start_y + self.__grid_height

                self.my_canvas.create_line(x, y, x, end, fill="black", width=2)

                self.my_canvas.create_text(x - 0.25 * self.__cell_size, y + 0.5 * (end - y), text=var_name, font=self.__normal_font, angle=90)

                y += 2 * self.__cell_size * 2**(magnitude + 1)
        
    def __draw_rect(self, x1: float, y1: float, x2: float, y2: float, col: str, openings: str, line_width: int) -> None:
        offset = 0.05 * self.__cell_size
        x1 += offset
        y1 += offset
        x2 -= offset
        y2 -= offset
        if "l" not in openings:
            self.my_canvas.create_line(x2, y1, x2, y2, fill=col, width=line_width)
        if "r" not in openings:
            self.my_canvas.create_line(x1, y1, x1, y2, fill=col, width=line_width)
        if "t" not in openings:
            self.my_canvas.create_line(x1, y2, x2, y2, fill=col, width=line_width)
        if "b" not in openings:
            self.my_canvas.create_line(x1, y1, x2, y1, fill=col, width=line_width)
    #endregion: Drawing
    #
    #
    #
    #region: Helper Methods
    def update_sizes(self) -> None:
        """
        Update the sizes of the cells based on the current canvas size.
        """
        if len(self.__vars) == 0:
            return
        num_top_vars = math.ceil(len(self.__vars) / 2)
        num_bottom_vars = math.floor(len(self.__vars) / 2)

        cell_width = self.__width / (self.dimensions[0] + num_top_vars)
        cell_height = self.__height / (self.dimensions[1] + num_bottom_vars)

        self.__cell_size = min(cell_width, cell_height)

        self.__large_font = (FONTS.TYPE, int(self.__cell_size // 2))
        self.__normal_font = (FONTS.TYPE, int(self.__cell_size // 4))
        self.__small_font = (FONTS.TYPE, int(self.__cell_size // 6))

        self.__grid_width = self.__cell_size * self.dimensions[0]
        self.__grid_height = self.__cell_size * self.dimensions[1]
        self.__start_x = (self.__width - self.__grid_width) / 2
        self.__start_y = (self.__height - self.__grid_height) / 2

        self.draw()
    
    def canvas_to_kv_index(self, x: float, y: float) -> int:
        """
        Convert canvas coordinates to Karnaugh map index.
        """
        new_x: int = int((x - self.__start_x) // self.__cell_size)
        new_y: int = int((y - self.__start_y) // self.__cell_size)

        if new_x < 0 or new_x >= self.dimensions[0] or new_y < 0 or new_y >= self.dimensions[1]:
            return -1

        return KV_Utils.CoordinateToIndex(new_x, new_y, len(self.__vars))
    
    def __get_rect_bounds(self, block: list[int], marking:list[int]) -> tuple[tuple[int, int], tuple[int, int], str]:
        get_tl_and_br: Callable[[tuple[int,int,int,int], tuple[int,int]], tuple[int,int,int,int]] = lambda x, y: (min(x[0], y[0]), min(x[1], y[1]), max(x[2], y[0]), max(x[3], y[1]))

        kv_max_x = self.dimensions[0] - 1
        kv_max_y = self.dimensions[1] - 1

        min_x, min_y, max_x, max_y = reduce(get_tl_and_br, [KV_Utils.IndexToCoordinate(i, len(self.__vars)) for i in block], (kv_max_x,kv_max_y,0,0))

        openings:  str = ""

        if min_x == 0 and KV_Utils.CoordinateToIndex(kv_max_x, min_y, len(self.__vars)) in marking:
            openings += "r"
        if max_x == self.dimensions[0] - 1 and KV_Utils.CoordinateToIndex(0, min_y, len(self.__vars)) in marking:
            openings += "l"
        if openings == "rl":
            openings = ""
        
        if min_y == 0 and KV_Utils.CoordinateToIndex(min_x, kv_max_y, len(self.__vars)) in marking:
            openings += "b"
        if max_y == self.dimensions[1] - 1 and KV_Utils.CoordinateToIndex(min_x, 0, len(self.__vars)) in marking:
            openings += "t"
        if openings.endswith("bt"):
            openings = openings[:-2]

        return ((min_x,min_y), (max_x,max_y), openings)
    #endregion: Helper Methods    
    #
    #
    #
    #region: Input Methods
    def new_marking(self) -> None:
        if len(self.__current_indices) == 0:
            return

        self.__markings[self.__marking_index] = (self.current_col.get(), self.__current_indices.copy())

        self.__current_indices.clear()

        self.__col_index += 1
        if self.__col_index >= len(self.col_map):
            self.__col_index = 0
        self.current_col.set(list(self.col_map.keys())[self.__col_index])
        
        self.__markings.insert(self.__marking_index + 1, (self.current_col, self.__current_indices))
        self.__marking_index += 1

    def different_marking(self, offset: int) -> None:
        self.__markings[self.__marking_index] = (self.current_col.get(), self.__current_indices.copy())

        if len(self.__current_indices) == 0 and len(self.__markings) > 1:
            self.__markings.pop(self.__marking_index)
        else:
            self.__marking_index += offset

        marking_len = len(self.__markings)
        if self.__marking_index < 0:
            self.__marking_index += marking_len
        elif self.__marking_index >= marking_len:
            self.__marking_index -= marking_len
        
        self.__current_indices = self.__markings[self.__marking_index][1].copy()

        val = self.__markings[self.__marking_index][0]

        assert isinstance(val, str), "val is not a String"

        self.current_col.set(val)

        self.__markings[self.__marking_index] = (self.current_col, self.__current_indices)
        self.draw()
    
    def get_kv_string(self) -> str:
        """
        Get the Karnaugh map string representation.
        """
        retval = KV_Utils.KARNAUGH_TEMPLATE

        #TODO: Generator for markings

        ovals: list[str] = []
        oval: list[str] = []

        for col, indices in self.__markings:
            if isinstance(col, StringVar):
                col = col.get()
            KV_Utils.make_blocks(indices, len(self.__vars))
            for block in KV_Utils.blocks:
                (x1, y1), (x2, y2), openings = self.__get_rect_bounds(block, indices)
                
                x = x1 if "r" in openings else (x2 + 1 if "l" in openings else (x2 + x1) / 2 + 0.5)
                y = y1 - 1 if "b" in openings else (y2 if "t" in openings else (y2 + y1) / 2 - 0.5)

                print(f"X: {x}, Y: {y}")

                y = self.dimensions[1] - y - 1

                delta_x = (x2 - x1 + 1) * (2 if "l" in openings or "r" in openings else 1) - 0.1
                delta_y = (y2 - y1 + 1) * (2 if "t" in openings or "b" in openings else 1) - 0.1

                side = f"[{openings}]" if openings else ""

                oval.append(KV_Utils.OVAL_TEMPLATE.format(
                    x=x,
                    y=y,
                    delta_x=delta_x,
                    delta_y=delta_y,
                    side=side
                ))
            
            ovals.append(KV_Utils.color_item("\n".join(oval), col))
            oval.clear()


        return retval. format(
            num_vars=len(self.__vars),
            title = self.title.get(),
            my_vars="".join(map(lambda x: "{{{}}}".format(x), reversed(self.__vars))),
            vals="".join(self.vals.get()),
            ovals="%\n".join(ovals)
        )
    #endregion: Input Methods