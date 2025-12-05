from tkinter import Canvas

class KVDrawable:
    def __init__(self, canvas: Canvas) -> None:
        self._canvas = canvas
    
    def _delete_item(self, item: int) -> None:
        self._canvas.delete(item)