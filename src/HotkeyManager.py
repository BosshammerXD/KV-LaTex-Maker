from __future__ import annotations
from collections.abc import Callable
from tkinter import Event, Tk
from enum import StrEnum, IntFlag

class ControlStates(IntFlag):
    NONE = 0x0000
    SHFT = 0x0001
    LOCK = 0x0002
    CTRL = 0x0004
    MOD1 = 0x0008
    MOD2 = 0x0010
    MOD3 = 0x0040
    MOD4 = 0x0080
    ALL  = 0x00DF

    @staticmethod
    def from_int(num: int) -> ControlStates:
        return ControlStates.ALL & num

class Hotkey(tuple[ControlStates, str]):
    def __new__(cls, state: int | ControlStates, keysym: str):
        if not isinstance(state, ControlStates):
            state = ControlStates.from_int(state)
        return super().__new__(cls, (state, keysym))
        
    
    @staticmethod
    def from_event(event: Event) -> Hotkey:
        assert(isinstance(event.state, int))
        return Hotkey(event.state, event.keysym)

class HotkeyActions(StrEnum):
    UNDO = "UNDO"
    REDO = "REDO"

class HotkeyManager:
    __selected: HotkeyManager | None = None
    listening_for_hotkey: Hotkey | None = None
    __last_state: ControlStates = ControlStates.NONE
    __hotkey_2_action: dict[Hotkey, HotkeyActions] = {}
    def __init__(self, root: Tk) -> None:
        self.__registered_funcs: dict[HotkeyActions, Callable[[Event, bool], None]] = {}
        root.bind("<KeyPressed>", self.__on_key_press)
    
    def register(self, action: HotkeyActions, func: Callable[[Event, bool], None]) -> None:
        if self.__registered_funcs.get(action) is not None:
            raise ValueError(f"{action} is already bound")
        self.__registered_funcs[action] = func

    def __on_key_press(self, event: Event) -> None:
        func = self.__get_func_from_event(event)
        if func is not None:
            func(event, True)

    @classmethod
    def init_hotkey_to_action(cls, values: dict[tuple[int, str], str]) -> None:
        assert(len(cls.__hotkey_2_action) == 0)
        added_actions: set[HotkeyActions] = set()
        for (ev, keysym), action_str in values.items():
            try:
                action = HotkeyActions[action_str]
                if action in added_actions:
                    raise ValueError(f"{action_str} has two hotkeys")
                added_actions.add(action)
                cls.__hotkey_2_action[Hotkey(ev, keysym)] = action
            except KeyError:
                raise ValueError(f"{action_str} is not a valid action")

    @classmethod
    def change_hotkey(cls, old_hotkey: Hotkey, new_hotkey: Hotkey) -> None:
        action: HotkeyActions = cls.__hotkey_2_action.pop(old_hotkey)
        cls.__hotkey_2_action[new_hotkey] = action

    @classmethod
    def on_key_press(cls, event: Event) -> None:
        if cls.__selected is not None:
            cls.__selected.__on_key_press(event)
        elif cls.listening_for_hotkey is not None:
            cls.__change_hotkey_ev(event, cls.listening_for_hotkey)

    @classmethod
    def __change_hotkey_ev(cls, event: Event, old_hotkey: Hotkey) -> None:
        assert(isinstance(event.state, int))
        if (cls.__last_state ^ event.state).bit_count() == 1:
            cls.__last_state = ControlStates.from_int(event.state)
        else:
            cls.__last_state = ControlStates.NONE
            cls.change_hotkey(old_hotkey, Hotkey.from_event(event))
    
    def __get_func_from_event(self, event: Event) -> Callable[[Event, bool], None] | None:
        action = self.__hotkey_2_action.get(Hotkey.from_event(event))
        if action is None:
            return None
        return self.__registered_funcs.get(action)