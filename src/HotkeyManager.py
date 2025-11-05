from collections.abc import Callable
from tkinter import Tk, Event, StringVar

class HotkeyManager:
    def __init__(self, master: Tk):
        self.master: Tk = master
        self.override_hotkey: str = ""
        self.hotkeys: dict[str, tuple[Callable[[], None], StringVar]] = {}
        self.stringvar_map: dict[str, str] = {}

        self.master.bind("<KeyPress>", self._on_hotkey) # type: ignore[override]
    
    def bind_hotkey(self, hotkey: StringVar, func: Callable[[], None]):
        self.stringvar_map[str(hotkey)] = hotkey.get()
        self.hotkeys[hotkey.get()] = func, hotkey

        hotkey.trace_add("write", lambda x,y,z: self.hotkey_changed(str(hotkey), hotkey.get()))
    
    def unbind_hotkey(self, hotkey: StringVar) -> None:
        self.stringvar_map.pop(str(hotkey), None)
        self.hotkeys.pop(hotkey.get(), None)
    
    def _on_hotkey(self, event: Event) -> None: #type: ignore[override]
        self.hotkeys.get(event.keysym, (lambda : None, StringVar()))[0]()

        
    
    def hotkey_changed(self, my_id: str, val:str) -> None:
        old_input = self.stringvar_map[my_id]
        self.stringvar_map[my_id] = val
        
        
        func_in_map = self.hotkeys.get(val)

        if func_in_map is None:
            holder = self.hotkeys.pop(old_input, (lambda : None, StringVar()))
            self.hotkeys[val] = holder
        else:
            old_func, old_hotkey = func_in_map

            holder = self.hotkeys.pop(old_input, (lambda : None, StringVar()))
            self.hotkeys[val] = holder

            self.hotkeys[old_input] = old_func, old_hotkey

            self.stringvar_map[str(old_hotkey)] = old_input
        
        
        

    