from JsonHandler import read_from_json, write_to_json
from .STATIC import PATHS
from . import DYNAMIC
from . import LANGUAGE

def load_config():
    def load_lang():
        try: 
            read_from_json("languages/" + DYNAMIC.Selected_language + ".json", LANGUAGE)
        except FileNotFoundError:
            #replace with pop up
            print(f"couldn't find language: {DYNAMIC.Selected_language} using ENGLISH as Default")

    try:
        read_from_json(PATHS.CONFIG_FILE, DYNAMIC)
    except FileNotFoundError:
        update_config(True)   
    except ValueError:
        #replace with pop-up that tells the user this
        print("Json does not have the correct format")
        update_config(True)
    
    load_lang()

def update_config(read: bool = False):
    write_to_json(PATHS.CONFIG_FILE, DYNAMIC)
    try:
        write_to_json(PATHS.CONFIG_FILE, DYNAMIC)
        if read:
            read_from_json(PATHS.CONFIG_FILE, DYNAMIC)
    except Exception as e:
        #replace with Popup that says "couldn't create/write to config file so config will not be saved" with answer option "Ok"
        print(f"couldn't create/write to config file.\nPath: {PATHS.CONFIG_FILE}")
        print(e)