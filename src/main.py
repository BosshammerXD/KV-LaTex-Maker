import tkinter as tk
from typing import Callable
from Globals import DYNAMIC
from KV_Diagramm.KVManager import KVManager
from KV_Diagramm.KVInputHandler import KVInputHandler
from UI.Menus.ColorMenu import ColorMenu
from UI.Section import Section
import Globals.LANGUAGE as lang
from Globals.STATIC import ROOT, BG_COLOR
from Globals.STATIC.DEF_KV_VALUES import VARS, VALUES
from Globals.Funcs import load_config, update_config

#region Menubar
def build_menubar():
    menu = tk.Menu(ROOT)
    #menu.add_command(label=lang.MENUBAR.SETTINGS, command=lambda: None)
    menu.add_command(label=lang.MENUBAR.COLORS, command=ColorMenu)
    ROOT.config(menu=menu)
#endregion
#
#
#
#region KV Diagram
def build_KV_Diagram() -> tuple[KVManager, KVInputHandler]:
    canvas = tk.Canvas(ROOT, bg=BG_COLOR)
    canvas.grid(row=0, column=0, sticky="nsew")
    kv_manager = KVManager(canvas)
    return kv_manager, KVInputHandler(canvas, kv_manager)
#endregion
#
#
#
#region Sidebar
def build_sidebar(kv_manager: KVManager, kv_input_handler: KVInputHandler):
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
        build_title_input_section(lang.SECTIONS.VAR_FRAME_NAME, vars_input)
        kv_input_handler.link_vars(vars_input) 
    
    def build_vals():
        vals = tk.StringVar(value=VALUES)
        build_title_input_section(lang.SECTIONS.VALS_FRAME_NAME, vals)
        kv_input_handler.link_vals(vals)

    def build_marking_select():
        marking_frame = Section(controls, lang.SECTIONS.MARKING_FRAME_NAME).frame

        colors = DYNAMIC.Colors.keys()

        option_menu = tk.OptionMenu(marking_frame, kv_manager.current_col, *colors)
        option_menu.pack(fill="x", pady=0)

        def set_strVar(var: tk.StringVar, val: str) -> Callable[[], None]:
            return lambda: var.set(val)
        def update_options():
            menu: tk.Menu = option_menu["menu"]
            menu.delete(0, "end")
            for opt in DYNAMIC.Colors.keys():
                menu.add_command(label=opt, command=set_strVar(kv_manager.current_col, opt))
            kv_manager.update_markings()
        kv_input_handler.link_marking_color(kv_manager.current_col)
        ROOT.bind("<<ColorsChanged>>", lambda _: update_options())

        next_prev_frame = tk.Frame(marking_frame)
        next_prev_frame.rowconfigure(0, weight=1)
        next_prev_frame.columnconfigure(0, weight=1)  # Left button (Prev.) gets more space
        next_prev_frame.columnconfigure(1, weight=1)  # Middle button (New) gets more space
        next_prev_frame.columnconfigure(2, weight=1)  # Right button (Next) gets more space
        next_prev_frame.pack(fill="x", pady=0)
        tk.Button(
            next_prev_frame, text=lang.PREVIOUS, 
            command=lambda : kv_manager.different_marking(-1)).grid(row=0, column=0, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=lang.NEW, 
            command=lambda : kv_manager.new_marking()).grid(row=0, column=1, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=lang.NEXT, 
            command=lambda : kv_manager.different_marking(1)).grid(row=0, column=2, sticky="ew", padx=0)

    def build_copy():
        def copy_to_clipboard():
            ROOT.clipboard_clear()
            ROOT.clipboard_append(kv_manager.get_kv_string())
            ROOT.update()  # Keeps the clipboard content after the program ends
        tk.Button(controls, text=lang.CPY_BUTTON, command=copy_to_clipboard).pack(fill="x", pady=5)

    build_title_input_section(lang.SECTIONS.TITLE_FRAME_NAME, kv_manager.title)
    build_vars()
    build_vals()
    build_marking_select()
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

    kv_manager, input_handler = build_KV_Diagram()

    build_sidebar(kv_manager, input_handler)  # Call the function to update the map

if __name__ == "__main__":
    load_config()

    build_ui()

    ROOT.mainloop()

    update_config()
#enregion