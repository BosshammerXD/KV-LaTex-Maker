from __future__ import annotations
from collections import deque
from collections.abc import Callable
from enum import Enum, auto
from tkinter import Event

class ActionTypes(Enum):
    CLEARED_FROM_REDO = auto()
    PUSHED_OUT_OF_QUEUE = auto()
    DO_ACTION = auto()
    UNDO_ACTION = auto()

_ActionType = Callable[[ActionTypes], None]

class UndoManager:
    __selected: UndoManager | None = None

    def __init__(self, reset_on_context_switch: bool = False, undo_buffer_len: int = 10) -> None:
        self.__undo_buffer_len = undo_buffer_len
        self.__reset_on_context_switch = reset_on_context_switch
        self.__redo_stack: list[_ActionType] = []
        self.__undo_queue: deque[_ActionType] = deque()

    @classmethod
    def switch_selected(cls, new_selected: UndoManager) -> None:
        if cls.__selected is not None and cls.__selected.__reset_on_context_switch:
            cls.__selected.reset()
        cls.__selected = new_selected

    def add_action(self, action: _ActionType, execute_do: bool = False) -> None:
        while self.__redo_stack:
            self.__redo_stack.pop()(ActionTypes.CLEARED_FROM_REDO)
        self.__undo_queue.append(action)
        if execute_do: action(ActionTypes.DO_ACTION)
        if len(self.__undo_queue) > self.__undo_buffer_len:
            self.__undo_queue.popleft()(ActionTypes.PUSHED_OUT_OF_QUEUE)
    
    @staticmethod
    def make_action(do: Callable[[], None] = lambda:None, undo: Callable[[], None]=lambda:None, redo_clr: Callable[[], None]=lambda:None, pushed_out: Callable[[], None]=lambda:None) -> _ActionType:
        def action(typ: ActionTypes) -> None:
            match typ:
                case ActionTypes.DO_ACTION:
                    do()
                case ActionTypes.UNDO_ACTION:
                    undo()
                case ActionTypes.CLEARED_FROM_REDO:
                    redo_clr()
                case ActionTypes.PUSHED_OUT_OF_QUEUE:
                    pushed_out()
        return action
    
    def undo(self) -> None:
        if self.__undo_queue:
            action = self.__undo_queue.pop()
            action(ActionTypes.UNDO_ACTION)
            self.__redo_stack.append(action)
    
    def redo(self) -> None:
        if self.__redo_stack:
            action = self.__redo_stack.pop()
            action(ActionTypes.DO_ACTION)
            self.__undo_queue.append(action)
    
    def reset(self) -> None:
        while self.__redo_stack:
            self.__redo_stack.pop()(ActionTypes.CLEARED_FROM_REDO)
        while self.__undo_queue:
            self.__undo_queue.popleft()(ActionTypes.PUSHED_OUT_OF_QUEUE)
    
    @classmethod
    def undo_ev(cls, ev: Event) -> None:
        if cls.__selected is not None:
            cls.__selected.undo()
    
    @classmethod
    def redo_ev(cls, ev: Event) -> None:
        if cls.__selected is not None:
            cls.__selected.redo()