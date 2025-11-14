from typing import Callable
from tkinter import Tk

ROOT: Tk = Tk()

BG_COLOR: str = "white"
LINE_COLOR: str = "black"
DEF_TEXT_COLOR: str = "black"
HIGHLIGHT_TEXT_COLOR: str = "yellow"
ACTION_STR_TO_FUNC: dict[str, Callable[[], None]] = {}