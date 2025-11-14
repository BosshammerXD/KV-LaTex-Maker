import tkinter as tk
from KV_Drawer import KV_Drawer
from UI.Section import Section
from UI.Popup import Popup
from Globals import LANGUAGE, STATIC, DYNAMIC, Funcs
from Globals.STATIC import DEF_KV_VALUES

#region Menubar
def build_menubar():
    menu = tk.Menu(STATIC.ROOT)
    options_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label=LANGUAGE.MENUBAR.OPTIONS, menu=options_menu)
    options_menu.add_command(label=LANGUAGE.MENUBAR.HOTKEYS, command=lambda: None)  # Placeholder for settings action
    options_menu.add_command(label=LANGUAGE.MENUBAR.HOTKEYS, command=lambda: None)  # Placeholder for colors action
    STATIC.ROOT.config(menu=menu)
#endregion
#
#
#
#region KV Diagram
def update_karnaugh_map(kv_drawer: KV_Drawer) -> None:
    kv_drawer.my_vars = DEF_KV_VALUES.VARS.split(",")
    
    kv_drawer.draw()

def build_KV_Diagram() -> KV_Drawer:
    canvas = tk.Canvas(STATIC.ROOT, bg=STATIC.BG_COLOR)
    canvas.grid(row=0, column=0, sticky="nsew")

    return KV_Drawer(canvas)  # Placeholder for KV_Drawer instance
#endregion
#
#
#
#region Sidebar
def build_sidebar(kv_drawer: KV_Drawer):
    # Controls on the right
    controls = tk.Frame(STATIC.ROOT)
    controls.grid(row=0, column=1, sticky="nsew")

    def build_title_input_section(title: str, value: tk.StringVar) -> tuple[Section, tk.Entry]:
        section = Section(controls, title)
        entry = tk.Entry(section.frame, textvariable=value)
        entry.pack(fill="x", pady=0)
        return section, entry

    def build_vars():
        vars_input = tk.StringVar(value=DEF_KV_VALUES.VARS)
        _, vars_entry = build_title_input_section(LANGUAGE.SECTIONS.VAR_FRAME_NAME, vars_input)

        var_warning = Popup(LANGUAGE.WARNING, LANGUAGE.VAR_WARNING_MSG)
        def set_vars(sure: bool = False) -> None:
            new_vars = vars_input.get().split(",")
            if len(new_vars) > 6 and not sure:
                var_warning.show()
                return
            kv_drawer.my_vars = new_vars
        var_warning.add_button(LANGUAGE.CONFIRM, lambda: set_vars(True))
        var_warning.add_button(LANGUAGE.DENY, lambda: None)
        vars_entry.bind("<Return>", lambda event: set_vars())  # Bind Enter key to set_vars

    def build_marking():
        marking_frame = Section(controls, LANGUAGE.SECTIONS.MARKING_FRAME_NAME).frame

        colors = DYNAMIC.Colors.keys()

        tk.OptionMenu(marking_frame, kv_drawer.current_col, *colors).pack(fill="x", pady=0)

        next_prev_frame = tk.Frame(marking_frame)
        next_prev_frame.rowconfigure(0, weight=1)
        next_prev_frame.columnconfigure(0, weight=1)  # Left button (Prev.) gets more space
        next_prev_frame.columnconfigure(1, weight=1)  # Middle button (New) gets more space
        next_prev_frame.columnconfigure(2, weight=1)  # Right button (Next) gets more space
        next_prev_frame.pack(fill="x", pady=0)
        tk.Button(
            next_prev_frame, text=LANGUAGE.PREVIOUS, 
            command=lambda : kv_drawer.different_marking(-1)).grid(row=0, column=0, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=LANGUAGE.NEW, 
            command=lambda : kv_drawer.new_marking()).grid(row=0, column=1, sticky="ew", padx=0)
        tk.Button(
            next_prev_frame, text=LANGUAGE.NEXT, 
            command=lambda : kv_drawer.different_marking(1)).grid(row=0, column=2, sticky="ew", padx=0)

    def build_copy():
        def copy_to_clipboard():
            STATIC.ROOT.clipboard_clear()
            STATIC.ROOT.clipboard_append(kv_drawer.get_kv_string())
            STATIC.ROOT.update()  # Keeps the clipboard content after the program ends
        tk.Button(controls, text=LANGUAGE.CPY_BUTTON, command=copy_to_clipboard).pack(fill="x", pady=5)

    build_title_input_section(LANGUAGE.SECTIONS.TITLE_FRAME_NAME, kv_drawer.title)
    build_vars()
    build_title_input_section(LANGUAGE.SECTIONS.VALS_FRAME_NAME, kv_drawer.vals)
    build_marking()
    build_copy()
    
    update_karnaugh_map(kv_drawer)  # Call the function to update the map
    STATIC.ROOT.mainloop()
#endregion
#
#
#
#region main
def build_ui():
    STATIC.ROOT.rowconfigure(0, weight=1)
    STATIC.ROOT.columnconfigure(0, weight=3)  # Left column (canvas) gets more space
    STATIC.ROOT.columnconfigure(1, weight=1)  # Right column (controls)

    kv_drawer = build_KV_Diagram()

    build_sidebar(kv_drawer)

if __name__ == "__main__":
    Funcs.load_config()

    build_ui()
#enregion