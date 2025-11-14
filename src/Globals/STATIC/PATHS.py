import os
import sys

def __get_app_dir():
    # Falls als exe mit PyInstaller/Frozen-Flag
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Normales Skript
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__BASE_DIR: str = __get_app_dir()

CONFIG_FOLDER: str = os.path.join(__BASE_DIR, "configs")
CONFIG_FILE: str = "config.json"