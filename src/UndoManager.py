from collections import deque
from collections.abc import Callable

class _ActionData:
    def __init__(self, do: Callable[[], None], undo: Callable[[], None]) -> None:
        self.__do = do
        self.__undo = undo
    
    def do(self):
        self.__do()
    
    def undo(self):
        self.__undo()

class UndoManager:
    def __init__(self, undo_buffer_len: int = 10) -> None:
        self.__redo_stack: list[_ActionData] = []
        self.__undo_queue: deque[_ActionData] = deque(maxlen=undo_buffer_len)
    
    def add_action(self, do: Callable[[], None], undo: Callable[[], None], execute_do: bool = False) -> None:
        self.__redo_stack.clear()
        self.__undo_queue.append(_ActionData(do, undo))
        if execute_do: do()
    
    def undo(self) -> None:
        if self.__undo_queue:
            action = self.__undo_queue.pop()
            action.undo()
            self.__redo_stack.append(action)
    
    def redo(self) -> None:
        if self.__redo_stack:
            action = self.__redo_stack.pop()
            action.do()
            self.__undo_queue.append(action)