#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
from bilibili import Package, Helper, Live

_standard_title = 'BiliBili Helper - ShadowMan'
_standard_window_size = (640, 480)

class GuiApplication(tk.Frame):
    
    def __init__(self, parent, async_loop = None):
        tk.Frame.__init__(self, parent, background = 'white')

        if async_loop is None:
            self.__async_loop = asyncio.get_event_loop()
        else:
            self.__async_loop = async_loop

        self.style = ttk.Style()

        self.__init_window()

    def __init_window(self):
        self.master.title(_standard_title)
        self.pack(fill = tk.BOTH, expand = True)
        self.__init_window_position(*_standard_window_size)
        self.__init_window_style()

        self.__init_window_ui()

    def __init_window_style(self):
        self.style.theme_use('default')
        self.style.configure('TButton', padding = (0, 5, 0, 5), font = 'Courier 12')

    def __init_window_ui(self):
        self.__init_window_menu_bar()
        self.__init_window_frame()

    def __init_window_menu_bar(self):
        self.__menu_bar = tk.Menu(self.master)
        self.master.config(menu = self.__menu_bar)

        file_menu = tk.Menu(self.__menu_bar, tearoff = False)
        file_menu.add_command(label = 'Load...', underline = 0)
        file_menu.add_command(label = 'Save...', underline = 0)

        view_menu = tk.Menu(self.__menu_bar, tearoff = False)
        view_sub_menu_side_bar = tk.Menu(view_menu, tearoff = False)
        view_sub_menu_side_bar.add_command(label = 'Hide Side Bar')
        view_menu.add_cascade(label = 'Side Bar', menu = view_sub_menu_side_bar)
        view_menu.add_command(label = 'Hide Status Bar')

        help_menu = tk.Menu(self.__menu_bar, tearoff = False)
        help_menu.add_command(label = 'Documents')
        help_menu.add_command(label = 'Weibo')
        help_menu.add_separator()
        help_menu.add_command(label = 'Open Source')
        help_menu.add_command(label='License')
        help_menu.add_separator()
        help_menu.add_command(label='Check For Update')
        help_menu.add_command(label='Changelog')
        help_menu.add_command(label='About')

        self.__menu_bar.add_cascade(label = 'File', menu = file_menu, underline = 0)
        self.__menu_bar.add_cascade(label = 'View', menu = view_menu, underline = 0)
        self.__menu_bar.add_cascade(label = 'Help', menu = help_menu, underline = 0)

    def __init_window_frame(self):
        self.__init_window_top_frame()
        self.__init_window_mid_frame()

    def __init_window_top_frame(self):
        top_frame = tk.Frame(self, background = '#fff', border = 1, relief = tk.SUNKEN)

        label = tk.Label(top_frame, text = 'http://live.bilibili.com/', background = '#fff', font = 'Fira\ Code')
        label.pack(side = tk.LEFT, padx = 3, pady = 3)

        self.live_room_id = tk.StringVar(self.master, '00000')
        entry = tk.Entry(top_frame, font = 'Fira\ Code', relief = tk.SUNKEN,
                         width = 30, textvariable = self.live_room_id)
        entry.pack(side = tk.LEFT, padx = 3, pady = 3)

        self.btn_text = tk.StringVar(self.master, 'Start')
        btn_start = tk.Button(top_frame, text = 'Start', font = 'Fira\ Code',
                         command = self.__startup, textvariable = self.btn_text)
        btn_start.pack(side = tk.LEFT, padx = 3, pady = 3)

        top_frame.pack(side = tk.TOP, fill = tk.X)

    def __init_window_mid_frame(self):
        mid_frame = tk.Frame(self, background = '#fff', border = 1, relief = tk.FLAT)

        text_dan_mu_message = tk.Text(mid_frame, font = 'Fira\ Code', cursor = 'trek')
        text_dan_mu_message.pack(fill = tk.BOTH, expand = True)
        self.dan_mu_message = text_dan_mu_message

        mid_frame.pack(fill = tk.BOTH, expand = True)

    def __startup(self):
        if not self.live_room_id.get():
            tk.messagebox.showwarning('Runtime Warning', 'live_room_id is none')
            return

        if not self.live_room_id.get().isdigit():
            tk.messagebox.showwarning('Runtime Warning', 'live_room_id must be integer')
            return
        tk.messagebox.showinfo('Listening', 'listening in {}'.format(self.live_room_id.get()))

        self.dan_mu_message.insert(tk.END, '[SYSTEM] Listening in {}\n'.format(self.live_room_id.get()))

    def __init_window_position(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x_coordinate = int((screen_width - width) / 2)
        y_coordinate = int((screen_height - height) / 2)

        self.master.geometry('{}x{}+{}+{}'.format(width, height, x_coordinate, y_coordinate))

if __name__ == '__main__':
    root_window = tk.Tk()
    main_frame = GuiApplication(root_window)

    root_window.mainloop()