from typing import Callable


class STATIC:
    class DEF_KV_VALUES:
        TITLE: str = ""
        VARS: str = "A,B,C,D"
        VALUES: str = "11000011****10**"
    class FONTS:
        class KV:
            TYPE: str = "Arial"
    BG_COLOR: str = "white"
    LINE_COLOR: str = "black"
    DEF_TEXT_COLOR: str = "black"
    HIGHLIGHT_TEXT_COLOR: str = "yellow"
    ACTION_STR_TO_FUNC: dict[str, Callable[[], None]] = {}

class DYNAMIC:
    HOTKEYS: dict[str, str] = {}
    COLORS: dict[str, str] = {
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "purple": "#800080",
        "cyan": "#00FFFF",
        "orange": "#FFA500",
        "pink": "#FFC0CB",
        "brown": "#A52A2A",
        "gray": "#808080",
    }
    SELECTED_LANGUAGE = "ENGLISH"

class LANGUAGE:
    CONFIRM: str = "Yes"
    DENY: str = "No"
    WARNING: str = "Warning"
    PREVIOUS: str = "Prev."
    NEW: str = "New"
    NEXT: str = "Next"

    VAR_WARNING_MSG: str = "entering more then 6 variables,\n can cause performance issues.\nProceed?"

    CPY_BUTTON: str = "Copy to clipboard"

    class SECTIONS:
        TITLE_FRAME_NAME: str = "Title"
        VAR_FRAME_NAME: str = "Variables"
        VALS_FRAME_NAME: str = "Values"
        MARKING_FRAME_NAME: str = "Marking"

    class MENUBAR:
        OPTIONS: str = "Options"
        HOTKEYS: str = "Hotkeys"
        COLORS: str = "Colors"
