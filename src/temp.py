from HotkeyManager import HotkeyManager
from tkinter import Tk, StringVar, ttk
import tkinter as tk

root = Tk()
root.geometry("300x200")

def popup_bonus():
    win = tk.Toplevel()
    win.wm_title("Window")

    l = tk.Label(win, text="Input")
    l.grid(row=0, column=0)

    b = ttk.Button(win, text="Okay", command=win.destroy)
    b.grid(row=1, column=0)



s1 = StringVar(value="a")
s2 = StringVar(value="b")

my_hotkey_manager = HotkeyManager(root)

my_hotkey_manager.bind_hotkey(s1, lambda: print("Hotkey 'a' pressed!"))
my_hotkey_manager.bind_hotkey(s2, lambda: print("Hotkey 'b' pressed!"))

s1.set("b")

popup_bonus()

root.mainloop()
