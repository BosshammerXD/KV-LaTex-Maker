import tkinter as tk
from tkinter import simpledialog

class SettingsDialog(tk.Toplevel):
    def __init__(self, master, hotkeys):
        super().__init__(master)
        self.hotkeys = hotkeys
        self.result = None
        self.label = tk.Label(self, text="Aktueller Hotkey: " + hotkeys.get("action", "Nicht gesetzt"))
        self.label.pack()
        self.button = tk.Button(self, text="Hotkey ändern", command=self.set_hotkey)
        self.button.pack()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_hotkey(self):
        self.label.config(text="Bitte Taste drücken...")
        self.grab_set()
        self.bind_all("<Key>", self.save_hotkey)

    def save_hotkey(self, event):
        key = event.keysym
        self.hotkeys["action"] = key
        self.label.config(text="Aktueller Hotkey: " + key)
        self.unbind_all("<Key>")
        self.grab_release()

    def on_close(self):
        self.result = self.hotkeys
        self.destroy()

# Hauptfenster
root = tk.Tk()
hotkeys = {"action": "F5"}

def open_settings():
    dialog = SettingsDialog(root, hotkeys)
    root.wait_window(dialog)
    # Hier ggf. Hotkeys neu binden

menu = tk.Menu(root)
settings_menu = tk.Menu(menu, tearoff=0)
settings_menu.add_command(label="Einstellungen", command=open_settings)
menu.add_cascade(label="Optionen", menu=settings_menu)
root.config(menu=menu)
root.mainloop()
