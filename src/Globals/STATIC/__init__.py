from typing import Callable
from tkinter import Tk
from UndoManager import UndoManager

ROOT: Tk = Tk()
MAIN_UNDO_MANAGER: UndoManager = UndoManager(reset_on_context_switch=False, undo_buffer_len=10)
SETTINGS_UNDO_MANAGER: UndoManager = UndoManager(reset_on_context_switch=True, undo_buffer_len=5)
UndoManager.switch_selected(MAIN_UNDO_MANAGER)

BG_COLOR: str = "white"
LINE_COLOR: str = "black"
DEF_TEXT_COLOR: str = "black"
HIGHLIGHT_TEXT_COLOR: str = "yellow"
ACTION_STR_TO_FUNC: dict[str, Callable[[], None]] = {}