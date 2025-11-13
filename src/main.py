import tkinter as tk
from KV_Drawer import KV_Drawer
from Section import Section
from Popup import Popup
from Globals import LANGUAGE, STATIC

root = tk.Tk()

def update_karnaugh_map(kv_drawer: KV_Drawer) -> None:
    # Beispielwerte für die Methode
    my_vars = STATIC.DEF_KV_VALUES.VALUES.split(",")

    kv_drawer.my_vars = my_vars
    
    kv_drawer.draw()

if __name__ == "__main__":
    menu = tk.Menu(root)
    
    options_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label=LANGUAGE.MENUBAR.OPTIONS, menu=options_menu)
    options_menu.add_command(label=LANGUAGE.MENUBAR.HOTKEYS, command=lambda: None)  # Placeholder for settings action
    options_menu.add_command(label=LANGUAGE.MENUBAR.HOTKEYS, command=lambda: None)  # Placeholder for colors action
    #root.config(menu=menu)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=3)  # Left column (canvas) gets more space
    root.columnconfigure(1, weight=1)  # Right column (controls)

    # Canvas on the left
    canvas = tk.Canvas(root, bg=STATIC.BG_COLOR)
    canvas.grid(row=0, column=0, sticky="nsew")

    my_KV_drawer = KV_Drawer(canvas)  # Placeholder for KV_Drawer instance

    # Controls on the right
    controls = tk.Frame(root)
    controls.grid(row=0, column=1, sticky="nsew")

    title_Frame = Section(controls, LANGUAGE.SECTIONS.TITLE_FRAME_NAME).frame
    tk.Entry(title_Frame, textvariable=my_KV_drawer.title).pack(fill="x", pady=0)

    # Arrange controls vertically inside the frame
    vars_input = tk.StringVar(value=STATIC.DEF_KV_VALUES.VALUES)
    var_frame = Section(controls, LANGUAGE.SECTIONS.VAR_FRAME_NAME).frame

    var_warning = Popup(LANGUAGE.WARNING, LANGUAGE.VAR_WARNING_MSG)
    def set_vars(sure: bool = False) -> None:
        new_vars = vars_input.get().split(",")
        if len(new_vars) > 6 and not sure:
            var_warning.show()
            return
        my_KV_drawer.my_vars = new_vars
    var_warning.add_button(LANGUAGE.CONFIRM, lambda: set_vars(True))
    var_warning.add_button(LANGUAGE.DENY, lambda: None)
    vars_entry = tk.Entry(var_frame, textvariable=vars_input)
    vars_entry.pack(fill="x", pady=0)
    vars_entry.bind("<Return>", lambda event: set_vars())  # Bind Enter key to set_vars



    vals_frame = Section(controls, LANGUAGE.SECTIONS.VALS_FRAME_NAME).frame
    tk.Entry(vals_frame, textvariable=my_KV_drawer.vals).pack(fill="x", pady=0)

    marking_frame = Section(controls, LANGUAGE.SECTIONS.MARKING_FRAME_NAME).frame

    colors = list(my_KV_drawer.col_map.keys())

    tk.OptionMenu(marking_frame, my_KV_drawer.current_col, *colors).pack(fill="x", pady=0)

    next_prev_frame = tk.Frame(marking_frame)
    next_prev_frame.rowconfigure(0, weight=1)
    next_prev_frame.columnconfigure(0, weight=1)  # Left button (Prev.) gets more space
    next_prev_frame.columnconfigure(1, weight=1)  # Middle button (New) gets more space
    next_prev_frame.columnconfigure(2, weight=1)  # Right button (Next) gets more space
    next_prev_frame.pack(fill="x", pady=0)
    tk.Button(
        next_prev_frame, text=LANGUAGE.PREVIOUS, 
        command=lambda : my_KV_drawer.different_marking(-1)).grid(row=0, column=0, sticky="ew", padx=0)
    tk.Button(
        next_prev_frame, text=LANGUAGE.NEW, 
        command=lambda : my_KV_drawer.new_marking()).grid(row=0, column=1, sticky="ew", padx=0)
    tk.Button(
        next_prev_frame, text=LANGUAGE.NEXT, 
        command=lambda : my_KV_drawer.different_marking(1)).grid(row=0, column=2, sticky="ew", padx=0)

    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(my_KV_drawer.get_kv_string())
        root.update()  # Keeps the clipboard content after the program ends
    tk.Button(controls, text=LANGUAGE.CPY_BUTTON, command=copy_to_clipboard).pack(fill="x", pady=5)

    update_karnaugh_map(my_KV_drawer)  # Call the function to update the map
    root.mainloop()