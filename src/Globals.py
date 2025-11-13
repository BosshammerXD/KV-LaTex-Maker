from typing import Callable
from JsonHandler import read_from_json, write_to_json
import os

__BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

class STATIC:
    class PATHS:
        CONFIG_FOLDER: str = os.path.join(__BASE_DIR, "configs")
        CONFIG_FILE: str = "config.json"
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
    Hotkeys: dict[str, str] = {}
    Colors: dict[str, str] = {
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
    Selected_language = "ENGLISH"

def load_config():
    try:
        read_from_json(STATIC.PATHS.CONFIG_FILE, DYNAMIC)
    except FileNotFoundError:
        update_config()
        read_from_json(STATIC.PATHS.CONFIG_FILE, DYNAMIC)
    except ValueError:
        #replace with pop-up that tells the user this
        print("Json does not have the correct format")
        update_config()
        read_from_json(STATIC.PATHS.CONFIG_FILE, DYNAMIC)
    
    try: 
        read_from_json(DYNAMIC.Selected_language + ".json", LANGUAGE)
    except FileNotFoundError:
        #replace with pop up
        print(f"couldn't find language: {DYNAMIC.Selected_language} using ENGLISH as Default")

def update_config():
    try:
        write_to_json(STATIC.PATHS.CONFIG_FILE, DYNAMIC)
    except:
        #replace with Popup that says "couldn't create/write to config file so config will not be saved" with answer option "Ok"
        print("couldn't create/write to config file")

class LANGUAGE:
    CONFIRM: str = "Yes"
    DENY: str = "No"
    WARNING: str = "Warning"
    PREVIOUS: str = "Prev."
    NEW: str = "New"
    NEXT: str = "Next"
    OK: str = "Ok"

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
