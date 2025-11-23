from tkinter import Canvas, Event, StringVar

from Globals import DYNAMIC
from Globals.STATIC.DEF_KV_VALUES import VALUES
from . import KVUtils
from .KVToLaTeX import get_kv_string

from .KVData import KVData, Marking
from .KVDrawer import KVDrawer


class KVManager:
    def __init__(self, canvas: Canvas) -> None:
        self.current_col: StringVar = StringVar(value=next(iter(DYNAMIC.Colors)))
        self.__col_index = 0
        self.title = StringVar(value="")
        values = StringVar(value=VALUES)
        values.trace_add("write", lambda x,y,z: self.kvdrawer.draw())
        self.kvdata = KVData(
            values
        )
        self.kvdata.markings.append(Marking(self.current_col.get(), DYNAMIC.Colors[self.current_col.get()]))
        self.kvdata.selected = 0
        self.kvdrawer = KVDrawer(canvas, self.kvdata)
        canvas.bind("<Button-1>", self.on_left_click)
        canvas.bind("<Button-3>", self.on_right_click)

    def on_left_click(self, event: Event) -> None:  # type: ignore[no-untyped-def]
        """
        Handle left mouse button click event.
        """
        index = self.kvdrawer.canvas_to_kv_index(event.x, event.y)
        current_marking = self.kvdata.get_selected_marking()
        current_indices = current_marking.indices
        if index == -1:
            return
        if len(current_indices) == 0:
            current_indices.append(index)
        else:
            neighbours = KVUtils.find_kv_neigbours(index, current_indices)
            try:
                neighbour = next(neighbours)
                different_bits = KVUtils.find_different_bits(index, neighbour)
                different_bit = next(different_bits)
            except StopIteration:
                return    
            try:
                next(different_bits)
                return
            except StopIteration:
                KVUtils.expand_block(current_indices, different_bit)

        self.kvdrawer.update_markingdata(current_marking, True)

    def on_right_click(self, event: Event) -> None:
        """
        Handle right mouse button click event.
        """
        current_marking = self.kvdata.get_selected_marking()
        current_indices = current_marking.indices
        if len(current_indices) == 0:
            return
        x = self.kvdrawer.canvas_to_kv_index(event.x, event.y)

        if x not in current_indices:
            print("Invalid click")
            return

        if len(current_indices) == 1:
            self.kvdrawer.remove_marking(current_marking)
            return

        index_in_current = current_indices.index(x)

        mid = len(current_indices) // 2
        relative_index: int
        if index_in_current < mid:
            relative_index = next(KVUtils.find_kv_neigbours(
                x, current_indices[mid:]))
            change = next(KVUtils.find_different_bits(x, relative_index))

            val = relative_index & (1 << change)

            current_indices[mid:] = list(
                filter(lambda x: x & (1 << change) == val, current_indices))
            current_indices[:mid] = []
        else:
            relative_index = next(KVUtils.find_kv_neigbours(
                x, current_indices[:mid]))
            change = next(KVUtils.find_different_bits(x, relative_index))

            val = relative_index & (1 << change)

            current_indices[:mid] = list(
                filter(lambda x: x & (1 << change) == val, current_indices))
            current_indices[mid:] = []
        self.kvdrawer.update_markingdata(current_marking)

    def get_kv_string(self) -> str:
        return get_kv_string(self.kvdata, self.title.get())


    def __build_marking(self) -> Marking:
        latex_col = self.current_col.get()
        tk_col = DYNAMIC.Colors.get(latex_col)
        assert(tk_col is not None)
        return Marking(latex_col, tk_col)

    def new_marking(self) -> None:
        current_indices = self.kvdata.get_selected_marking().indices
        if len(current_indices) == 0:
            return

        self.__col_index += 1
        if self.__col_index >= len(DYNAMIC.Colors):
            self.__col_index = 0
        self.current_col.set(list(DYNAMIC.Colors.keys())[self.__col_index])
        
        self.kvdata.selected += 1
        self.kvdata.markings.insert(self.kvdata.selected, self.__build_marking())
        self.kvdrawer.draw()
        

    def different_marking(self, offset: int) -> None:
        current_indices = self.kvdata.get_selected_marking().indices
        if len(current_indices) == 0 and len(self.kvdata.markings) > 1:
            self.kvdrawer.remove_marking(
                self.kvdata.markings.pop(self.kvdata.selected)
            )
        else:
            self.kvdata.selected += offset

        marking_len = len(self.kvdata.markings)
        if self.kvdata.selected < 0:
            self.kvdata.selected += marking_len
        elif self.kvdata.selected >= marking_len:
            self.kvdata.selected -= marking_len

        val = self.kvdata.markings[self.kvdata.selected].latex_color

        self.current_col.set(val)
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
            self.kvdata.markings.append(self.__build_marking())