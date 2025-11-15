from __future__ import annotations
from tkinter import Toplevel, Label, Frame, Button
import Globals.LANGUAGE as lang
from Globals import DYNAMIC
from Globals.STATIC import ROOT
from UI.ScrollingFrame import ScrollingFrame

class ColorMenu(Toplevel):
    class ColorItem(Frame):
        def __init__(self, master: ScrollingFrame, color_name: str, color_value: str, colors: dict[str, ColorMenu.ColorItem]):
            super().__init__(master, border=5, relief="groove")
            def btn_func():
                master.remove_child(self)
                colors.pop(self.name)
                self.destroy()

            self.name = color_name
            self.value = color_value

            self.rowconfigure(0,weight=1)
            for col in range(3):
                self.columnconfigure(col,weight=1, uniform="group1")

            Label(self, text=color_name).grid(column=0, row=0, sticky="nswe")
            Label(self, text=color_value, fg=color_value).grid(column=1, row=0, sticky="nswe")
            #TODO: Intergrate into Language Globals and Json
            Button(self, text="remove", command=btn_func).grid(column=2, row=0, sticky="nswe")
    
    def __init__(self) -> None:
        self.colors: dict[str, ColorMenu.ColorItem] = {}
        super().__init__(ROOT)
        self.deiconify()
        self.wm_title(lang.MENUBAR.COLORS)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1, uniform="group1")
        self.rowconfigure(1, weight=5, uniform="group1")
        self.rowconfigure(2, weight=1, uniform="group1")

        #TODO: Intergrate into Language Globals and Json
        label = Label(self, text="here you can add/remove colors for the markings in th KV Diagramm.\nIf you add a color make sure that color is Defined in Latex.")
        label.grid(column=0,row=0)

        self.__generate_color_list()
        self.__make_close_buttons()

    def __make_close_buttons(self):
        close_btns_frame: Frame = Frame(self)
        close_btns_frame.rowconfigure(0,weight=1)
        close_btns_frame.columnconfigure(0, weight=1)
        close_btns_frame.columnconfigure(1, weight=1)

        #TODO: Intergrate into Language Globals and Json
        Button(close_btns_frame, text="Apply", command=self.__apply).grid(column=0, row=0, sticky="nswe")
        def apply_and_close():
            self.__apply()
            self.destroy()
        #TODO: Intergrate into Language Globals and Json
        Button(
            close_btns_frame, 
            text="Apply and Close", 
            command=apply_and_close
        ).grid(column=1, row=0, sticky="nswe")
        close_btns_frame.grid(column=0,row=2, sticky="nswe")

    def __generate_color_list(self):
        self.col_list_frame = ScrollingFrame(self)
        self.bind("<Configure>", lambda _: self.col_list_frame.render())
        for col_name, col_val in DYNAMIC.Colors.items():
            col_item =  ColorMenu.ColorItem(
                self.col_list_frame, col_name, col_val, self.colors
            )
            self.colors[col_name] = col_item
            self.col_list_frame.add_child(col_item)
        self.col_list_frame.grid(column=0,row=1, sticky="nswe")

    def __apply(self):
        DYNAMIC.Colors.clear()
        for colitem in self.colors.values():
            DYNAMIC.Colors[colitem.name] = colitem.value
        ROOT.event_generate("<<ColorsChanged>>")