from dataclasses import dataclass, field
from typing import Iterator

from Globals import DYNAMIC

from .Marking import Marking
from Shapes.KVMarkings import KVMarkings

@dataclass
class KVData:
    _kv_markings: KVMarkings
    vals: str
    vars: list[str]
    _selected: int = -1
    width: int = 0
    height: int = 0
    _markings: list[Marking] = field(default_factory=lambda: [])

    @property
    def selected(self) -> int:
        return self._selected
    @selected.setter
    def selected(self, val: int) -> None:
        self._selected = val
        self.__adjust_selected()
        self._kv_markings.update_selected(self._selected)
    @property
    def markings(self) -> Iterator[Marking]:
        return iter(self._markings)
    @property
    def len_markings(self) -> int:
        return len(self._markings)

    def add_marking(self, latex_color: str, tag: str, index: int = -1) -> None:
        marking = Marking(latex_color, tag)
        if index < 0:
            self._markings.append(marking)
            self._kv_markings.new_marking(self.len_markings - 1, marking)
        else:
            self._markings.insert(index, marking)
            self._kv_markings.new_marking(index, marking)

    def remove_marking(self, index: int):
        marking = self._markings.pop(index)
        self._kv_markings.delete_marking(index, marking.TAG)
        self.__adjust_selected()

    def __adjust_selected(self) -> None:
        if not self._markings:
            self._selected = -1
        else:
            while self._selected < 0:
                self._selected += len(self._markings)
            while self._selected >= len(self._markings):
                self._selected -= len(self._markings)
        self._kv_markings.update_selected(self._selected)

    def get_num_vars(self) -> int:
        return len(self.vars)
    
    def get_selected_marking(self) -> Marking:
        return self._markings[self.selected]
    
    def update_colors(self):
        [self.remove_marking(i) for i, m in enumerate(self._markings) if m.latex_color not in DYNAMIC.Colors]