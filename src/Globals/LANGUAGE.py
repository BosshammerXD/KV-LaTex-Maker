CONFIRM: str = "Yes"
DENY: str = "No"
WARNING: str = "Warning"
INFO: str = "Info"
PREVIOUS: str = "Prev."
NEW: str = "New"
NEXT: str = "Next"
OK: str = "Ok"
APPLY: str = "Apply"
APPLY_AND_CLOSE: str = "Apply and close"
REMOVE: str = "Remove"
ERROR: str = "Error"

VAR_WARNING_MSG: str = "entering more then 6 variables,\n can cause performance issues.\nProceed?"

CPY_BUTTON: str = "Copy to clipboard"

class SECTIONS:
    TITLE_FRAME_NAME: str = "Title"
    VAR_FRAME_NAME: str = "Variables"
    VALS_FRAME_NAME: str = "Values"
    MARKING_FRAME_NAME: str = "Marking"

class MENUBAR:
    OPTIONS: str = "Options"
    SETTINGS: str = "Settings"
    COLORS: str = "Colors"

class COLORS_MENU:
    DESCRIPTION: str = "here you can add/remove colors for the markings in th KV Diagramm.\nIf you add a color make sure that color is Defined in Latex."
    COLOR: str = "Color"
    INVALID_COLOR: str = "\"{hex_col}\" is not a valid hex Color\nPlease use the format \"#RRGGBB\".\nWhere:\n  RR = Amount of Red\n  GG = Amount of Green\n  BB = Amount of Blue\nwith 00 being None and FF being the most"
    COLOR_EXISTS: str = "the Color \"{col_name}\" already exists.\nIf you want to overide it please remove it and add again."