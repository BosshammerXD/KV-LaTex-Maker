from tkinter import Canvas, Event, StringVar

from Globals import DYNAMIC
from Globals.STATIC.DEF_KV_VALUES import VALUES
from . import KV_Utils
from .KVToLaTeX import get_kv_string

from .KVData import KVData, Marking
from .KVDrawer import KVDrawer


class KVManager:
    def __init__(self, canvas: Canvas) -> None:
        self.current_col: StringVar = StringVar(value=DYNAMIC.Colors.__iter__().__next__())
        self.__col_index = 0
        values = StringVar(value=VALUES)
        values.trace_add("write", lambda x,y,z: self.kvdrawer.draw())
        self.kvdata = KVData(
            StringVar(value=""),
            values
        )
        self.kvdata.markings.append(Marking([], [], self.current_col.get(), DYNAMIC.Colors[self.current_col.get()]))
        self.kvdata.selected = 0
        self.kvdrawer = KVDrawer(canvas, self.kvdata)
        canvas.bind("<Button-1>", self.on_click)
        canvas.bind("<Button-3>", self.on_right_click)

    def on_click(self, event: Event) -> None:  # type: ignore[no-untyped-def]
        """
        Handle left mouse button click event.
        """

        index = self.kvdrawer.canvas_to_kv_index(event.x, event.y)
        current_indices = self.kvdata.markings[self.kvdata.selected].indices
        if index == -1:
            print("Invalid click")
            return
        if len(current_indices) == 0:
            self.kvdata.selected = len(self.kvdata.markings)
            latex_col = self.current_col.get()
            self.kvdata.markings.append(self.build_marking([index], latex_col))
            self.kvdrawer.draw()
            return

        neighbours = KV_Utils.find_kv_neigbours(index, current_indices)
        if len(neighbours) == 0:
            print("No neighbours")
            return
        different_bits = KV_Utils.find_different_bits(index, neighbours[0])
        if len(different_bits) != 1:
            print("Not a neighbour")
            return

        new_vals = [index]

        for val in current_indices:
            if val == neighbours[0]:
                continue
            val = val ^ (1 << different_bits[0])
            new_vals.append(val)

        current_indices.extend(new_vals)
        self.kvdata.markings[self.kvdata.selected].drawables = self.kvdrawer.indices_to_markingdata(current_indices)
        self.kvdrawer.draw()

    # type: ignore[no-untyped-def]
    def on_right_click(self, event: Event) -> None:
        """
        Handle right mouse button click event.
        """
        if self.kvdata.selected < 0:
            return
        x = self.kvdrawer.canvas_to_kv_index(event.x, event.y)
        current_indices = self.kvdata.markings[self.kvdata.selected].indices

        if x not in current_indices:
            print("Invalid click")
            return

        if len(current_indices) == 1:
            self.kvdrawer.remove_marking(
                self.kvdata.markings.pop(self.kvdata.selected)
            )
            return

        index_in_current = current_indices.index(x)

        mid = len(current_indices) // 2
        relative_index: int
        if index_in_current < mid:
            relative_index = KV_Utils.find_kv_neigbours(
                x, current_indices[mid:])[0]
            change = KV_Utils.find_different_bits(x, relative_index)[0]

            val = relative_index & (1 << change)

            current_indices[mid:] = list(
                filter(lambda x: x & (1 << change) == val, current_indices))
            current_indices[:mid] = []
        else:
            relative_index = KV_Utils.find_kv_neigbours(
                x, current_indices[:mid])[0]
            change = KV_Utils.find_different_bits(x, relative_index)[0]

            val = relative_index & (1 << change)

            current_indices[:mid] = list(
                filter(lambda x: x & (1 << change) == val, current_indices))
            current_indices[mid:] = []
        self.kvdrawer.draw()

    def get_kv_string(self) -> str:
        return get_kv_string(self.kvdata)


    def build_marking(self, indices: list[int], latex_color: str) -> Marking:
        drawables = self.kvdrawer.indices_to_markingdata(indices)
        tk_col = DYNAMIC.Colors.get(latex_color)
        assert(tk_col is not None)
        return Marking(indices, drawables, latex_color, tk_col)

    #TODO: Move
    def new_marking(self) -> None:
        current_indices = self.kvdata.markings[self.kvdata.selected].indices
        if len(current_indices) == 0:
            return

        #self.kvdata.markings[self.kvdata.selected] = (self.current_col.get(), current_indices.copy())

        #self.__current_indices.clear()

        self.__col_index += 1
        if self.__col_index >= len(DYNAMIC.Colors):
            self.__col_index = 0
        self.current_col.set(list(DYNAMIC.Colors.keys())[self.__col_index])
        
        self.kvdata.selected += 1
        self.kvdata.markings.insert(self.kvdata.selected, self.build_marking([], self.current_col.get()))
        

    def different_marking(self, offset: int) -> None:
        #self.__markings[self.__marking_index] = (self.current_col.get(), self.__current_indices.copy())
        current_indices = self.kvdata.markings[self.kvdata.selected].indices
        if len(current_indices) == 0 and len(self.kvdata.markings) > 1:
            self.kvdata.markings.pop(self.kvdata.selected)
        else:
            self.kvdata.selected += offset

        marking_len = len(self.kvdata.markings)
        if self.kvdata.selected < 0:
            self.kvdata.selected += marking_len
        elif self.kvdata.selected >= marking_len:
            self.kvdata.selected -= marking_len
        
        #self.__current_indices = self.__markings[self.__marking_index][1].copy()

        val = self.kvdata.markings[self.kvdata.selected].latex_color

        assert isinstance(val, str), "val is not a String"

        self.current_col.set(val)

        self.kvdata.markings[self.kvdata.selected] = self.build_marking(current_indices, self.current_col.get())
        self.kvdrawer.draw()
    
    def update_markings(self) -> None:
        """
        Removes all Markings that have a color that no longer exists
        """
        self.kvdata.markings = [
            m for m in self.kvdata.markings if m.latex_color in DYNAMIC.Colors.keys()
        ]
        if len(self.kvdata.markings):
            col = self.kvdata.markings[0].latex_color
            self.current_col.set(col)
            self.kvdata.selected = 0
            self.kvdrawer.draw()
        else:
            self.kvdata.selected = 0
            self.current_col.set(DYNAMIC.Colors.__iter__().__next__())
            self.kvdata.markings.append(self.build_marking([], self.current_col.get()))