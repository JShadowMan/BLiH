#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import time
import asyncio
import tkinter as tk
import threading
import tkinter.ttk as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from bilibili import Package, Helper, Live

_standard_title = 'BiliBili Helper - ShadowMan'
_standard_window_size = (640, 480)

class MessageHandler(Package.PackageHandlerProtocol):

    def __init__(self, async_loop, output_buffer):
        super(MessageHandler, self).__init__()

        self._async_loop = async_loop
        self._output_buffer = output_buffer

    def on_welcome_message(self, contents):
        pass

    def on_allow_join(self):
        self._output_buffer.insert(tk.END, '[SYSTEM] Join Live Room Success.\n')
        return True

    def on_heartbeat_response(self, contents):
        pass

    def on_gift_message(self, contents):
        pass

    def on_error_occurs(self, package):
        pass

    def on_dan_mu_message(self, contents):
        print(contents.message)
        self._output_buffer.insert('1.0', '[MESSAGE] {}: {}\n'.format(contents.name, contents.message))

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
        self.__init_window_tool_bar()
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

    def __init_window_tool_bar(self):
        tool_bar = tk.Frame(self, relief = tk.RAISED)

        tool_bar.grid_columnconfigure(0, weight = True)
        tool_bar.grid_columnconfigure(1, weight = True)
        tool_bar.grid_columnconfigure(2, weight = True)
        tool_bar.grid_columnconfigure(3, weight=True)

        image_msg = Image.open('resources/message.png')
        image_msg_tk = ImageTk.PhotoImage(image_msg)
        btn_message = tk.Button(tool_bar, image = image_msg_tk, relief = tk.FLAT)
        btn_message.image = image_msg_tk
        btn_message.grid(row = 0, column = 0)

        image_gift = Image.open('resources/gift.png')
        image_gift_tk = ImageTk.PhotoImage(image_gift)
        btn_gift = tk.Button(tool_bar, image = image_gift_tk, relief = tk.FLAT)
        btn_gift.image = image_gift_tk
        btn_gift.grid(row = 0, column = 1)

        image_list = Image.open('resources/list.png')
        image_list_tk = ImageTk.PhotoImage(image_list)
        btn_list = tk.Button(tool_bar, image = image_list_tk, relief = tk.FLAT)
        btn_list.image = image_list_tk
        btn_list.grid(row = 0, column = 2)

        image_ban = Image.open('resources/ban.png')
        image_ban_tk = ImageTk.PhotoImage(image_ban)
        btn_ban = tk.Button(tool_bar, image = image_ban_tk, relief = tk.FLAT)
        btn_ban.image = image_ban_tk
        btn_ban.grid(row = 0, column = 3)

        tool_bar.pack(side = tk.TOP, fill = tk.X)

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

        live_room_id = int(self.live_room_id.get())
        if self.btn_text.get() == 'Start':
            self.dan_mu_message.insert(tk.END, '[SYSTEM] Listening In Live-{}\n'.format(live_room_id))
        else:
            self.dan_mu_message.insert(tk.END, '[SYSTEM] Stop Listening For Live-{}\n'.format(live_room_id))
        self.btn_text.set('Stop' if self.btn_text.get() == 'Start' else 'Start')

        return asyncio.ensure_future(self.__listen_live_room(live_room_id))

    async def __listen_live_room(self, live_room_id):
        await Live.LiveBiliBili(loop = self.__async_loop).listen(live_room_id, MessageHandler,
                                                                 self.__async_loop, self.dan_mu_message)

    def __init_window_position(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x_coordinate = int((screen_width - width) / 2)
        y_coordinate = int((screen_height - height) / 2)

        self.master.geometry('{}x{}+{}+{}'.format(width, height, x_coordinate, y_coordinate))

async def main():
    root_window = tk.Tk()
    main_frame = GuiApplication(root_window)

    async def run_gui(root, interval=0.05):
        try:
            while True:
                root.update()
                await asyncio.sleep(interval)
        except tk.TclError as e:
            if "application has been destroyed" not in e.args[0]:
                raise

    await run_gui(root_window)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())