from FileManagement.JsonHandler import read_from_json, write_to_json
from .STATIC import PATHS
from . import DYNAMIC
from . import LANGUAGE
from UI.Popup import Popup

def load_config():
    def load_lang():
        try: 
            read_from_json("languages/" + DYNAMIC.Selected_language + ".json", LANGUAGE)
        except FileNotFoundError:
            LANG_NOT_FOUND_POP_UP: Popup = Popup("Info", f"Was Not able to find the {DYNAMIC.Selected_language} Language Package.\nSwitching to Default Language English")
            LANG_NOT_FOUND_POP_UP.add_button("Ok", lambda: None)
            LANG_NOT_FOUND_POP_UP.show()

    try:
        read_from_json(PATHS.CONFIG_FILE, DYNAMIC)
    except FileNotFoundError:
        JSON_NOT_FOUND_POP_UP: Popup = Popup("Info", "Could not find config.json\nWill generate new config.json")
        JSON_NOT_FOUND_POP_UP.add_button("Ok", lambda: None)
        JSON_NOT_FOUND_POP_UP.show()
        update_config(True)   
    except ValueError:
        JSON_WRONG_POP_UP: Popup = Popup("Info", "The found config.json has the wrong format.\nIt will be deleted and replaced by new config.json.")
        JSON_WRONG_POP_UP.add_button("Ok", lambda: None)
        JSON_WRONG_POP_UP.show()
        update_config(True)
    
    load_lang()

def update_config(read: bool = False):
    try:
        write_to_json(PATHS.CONFIG_FILE, DYNAMIC)
        if read:
            read_from_json(PATHS.CONFIG_FILE, DYNAMIC)
    except:
        JSON_NOT_WRIDDEN_POP_UP: Popup = Popup("Info", "Couldn't create/modify the config.json.\nThis means your Changes will not be saved")
        JSON_NOT_WRIDDEN_POP_UP.add_button("Ok", lambda: None)
        JSON_NOT_WRIDDEN_POP_UP.show()