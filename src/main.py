import tkinter as tk
from typing import Callable
from Globals import DYNAMIC
from KV_Diagramm.KVManager import KVManager
from KV_Diagramm.KVManager import KVManager
from UI.Menus.ColorMenu import ColorMenu
from UI.Section import Section
from UI.Popup import Popup
import Globals.LANGUAGE as lang
from Globals.STATIC import ROOT, BG_COLOR
from Globals.STATIC.DEF_KV_VALUES import VARS
from Globals.Funcs import load_config, update_config

#region Menubar
def build_menubar():
    menu = tk.Menu(ROOT)
    #menu.add_command(label=lang.MENUBAR.SETTINGS, command=lambda: None)  # Placeholder for settings action
    menu.add_command(label=lang.MENUBAR.COLORS, command=ColorMenu)  # Placeholder for colors action
    ROOT.config(menu=menu)
#endregion
#
#
#
#region KV Diagram
def update_karnaugh_map(KVManager: KVManager) -> None:
    KVManager.kvdata.vars = VARS.split(",")
    KVManager.kvdrawer.update_sizes()
    KVManager.kvdrawer.draw()

def build_KV_Diagram() -> KVManager:
    canvas = tk.Canvas(ROOT, bg=BG_COLOR)
    canvas.grid(row=0, column=0, sticky="nsew")

    return KVManager(canvas)  # Placeholder for KVManager instance
#endregion
#
#
#
#region Sidebar
def build_sidebar(KVManager: KVManager):
    # Controls on the right
    controls = tk.Frame(ROOT)
    controls.grid(row=0, column=1, sticky="nsew")

    def build_title_input_section(title: str, value: tk.StringVar) -> tuple[Section, tk.Entry]:
        section = Section(controls, title)
        entry = tk.Entry(section.frame, textvariable=value)
        entry.pack(fill="x", pady=0)
        return section, entry

    def build_vars():
        vars_input = tk.StringVar(value=VARS)
        _, vars_entry = build_title_input_section(lang.SECTIONS.VAR_FRAME_NAME, vars_input)

        var_warning = Popup(lang.WARNING, lang.VAR_WARNING_MSG)
        def set_vars(sure: bool = False) -> None:
            new_vars = vars_input.get().split(",")
            if len(new_vars) > 6 and not sure:
                var_warning.show()
                return
            KVManager.kvdata.vars = new_vars
            KVManager.kvdrawer.update_sizes()
            KVManager.kvdrawer.draw()
        var_warning.add_button(lang.CONFIRM, lambda: set_vars(True))
        var_warning.add_button(lang.DENY, lambda: None)
        vars_entry.bind("<Return>", lambda event: set_vars())  # Bind Enter key to set_vars

    def build_marking():
        marking_frame = Section(controls, lang.SECTIONS.MARKING_FRAME_NAME).frame

        colors = DYNAMIC.Colors.keys()

        option_menu = tk.OptionMenu(marking_frame, KVManager.current_col, *colors)
        option_menu.pack(fill="x", pady=0)

        def set_strVar(var: tk.StringVar, val: str) -> Callable[[], None]:
            return lambda: var.set(val)
        def update_options():
            menu: tk.Menu = option_menu["menu"]
            menu.delete(0, "end")
            for opt in DYNAMIC.Colors.keys():
                menu.add_command(label=opt, command=set_strVar(KVManager.current_col, opt))
            KVManager.update_markings()
        ROOT.bind("<<ColorsChanged>>", lambda _: update_options())

        next_prev_frame = tk.Frame(marking_frame)
        next_prev_frame.rowconfigure(0, weight=1)
        next_prev_frame.columnconfigure(0, weight=1)  # Left button (Prev.) gets more space
        next_prev_frame.columnconfigure(1, weight=1)  # Middle button (New) gets more space
        next_prev_frame.columnconfigure(2, weight=1)  # Right button (Next) gets more space
        next_prev_frame.pack(fill="x", pady=0)
        tk.Button(
            next_prev_frame, text=lang.PREVIOUS, 
            command=lambda : KVManager.different_marking(-1)).grid(row=0, column=0, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=lang.NEW, 
            command=lambda : KVManager.new_marking()).grid(row=0, column=1, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=lang.NEXT, 
            command=lambda : KVManager.different_marking(1)).grid(row=0, column=2, sticky="ew", padx=0)

    def build_copy():
        def copy_to_clipboard():
            ROOT.clipboard_clear()
            ROOT.clipboard_append(KVManager.get_kv_string())
            ROOT.update()  # Keeps the clipboard content after the program ends
        tk.Button(controls, text=lang.CPY_BUTTON, command=copy_to_clipboard).pack(fill="x", pady=5)

    build_title_input_section(lang.SECTIONS.TITLE_FRAME_NAME, KVManager.kvdata.title)
    build_vars()
    build_title_input_section(lang.SECTIONS.VALS_FRAME_NAME, KVManager.kvdata.vals)
    build_marking()
    build_copy()
#endregion
#
#
#
#region main
def build_ui():
    ROOT.rowconfigure(0, weight=1)
    ROOT.columnconfigure(0, weight=3)  # Left column (canvas) gets more space
    ROOT.columnconfigure(1, weight=1)  # Right column (controls)

    build_menubar()

    KVManager = build_KV_Diagram()

    build_sidebar(KVManager)

    ROOT.after_idle(lambda: update_karnaugh_map(KVManager))  # Call the function to update the map

if __name__ == "__main__":
    load_config()

    build_ui()

    ROOT.mainloop()

    update_config()
#enregion