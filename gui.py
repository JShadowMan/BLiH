#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
import tkinter
import threading
from tkinter import ttk
from bilibili import Package, Helper, Live

standard_title = 'BiliBili Helper - ShadowMan'
standard_window_size = (640, 480)

class MessageHandler(Package.PackageHandlerProtocol):

    def __init__(self):
        super().__init__()

    def on_allow_join(self):
        print('join live room succeed')
        return True

    def on_dan_mu_message(self, contents):
        print(contents)

    def on_error_occurs(self, package):
        pass

    def on_gift_message(self, contents):
        print(contents)

    def on_heartbeat_response(self, contents):
        print(contents)

    def on_welcome_message(self, contents):
        print(contents)

class GuiApplication(tkinter.Frame):
    
    def __init__(self, parent, async_loop = None):
        tkinter.Frame.__init__(self, parent, background = 'white')

        if async_loop is None:
            self.__async_loop = asyncio.get_event_loop()
        else:
            self.__async_loop = async_loop

        self.parent = parent
        self.style = tkinter.ttk.Style()

        self.__init_window()

    def __init_window(self):
        self.parent.title(standard_title)
        self.pack(fill = tkinter.BOTH, expand = 1)
        self.__init_window_position(*standard_window_size)
        self.__init_window_style()

        self.__init_window_ui()

    def __init_window_style(self):
        self.style.theme_use('default')
        self.style.configure('TButton', padding = (0, 5, 0, 5), font = 'Courier 12')

    def __init_window_ui(self):
        self.pack(fill = tkinter.BOTH, expand = True)

        top_frame = tkinter.Frame(self)
        top_frame.pack(fill = tkinter.X, side = tkinter.TOP)

        label_href_prefix = ttk.Label(top_frame, text = 'http://live.bilibili.com/')
        label_href_prefix.pack(side = tkinter.LEFT, padx = 5, pady = 5)

        entry_value = tkinter.StringVar(top_frame)
        entry_live_room_id = ttk.Entry(top_frame, textvariable = entry_value)
        entry_live_room_id.pack(side = tkinter.LEFT, padx = 5, pady = 5)

        btn_stop = ttk.Button(top_frame, text = 'Stop', command = self.stop)
        btn_stop.pack(side = tkinter.RIGHT, padx = 5, pady = 5)

        btn_start = ttk.Button(top_frame, text = 'Start', command = self.start)
        btn_start.pack(side = tkinter.RIGHT, padx = 5, pady = 5)

        mid_frame = tkinter.Frame(self)
        mid_frame.pack(fill = tkinter.BOTH, expand = True)

        text_value = tkinter.StringVar(mid_frame)
        text_message = tkinter.Text(mid_frame)
        text_message.pack(fill = tkinter.BOTH, expand = True)

        bot_frame = tkinter.Frame(self)
        bot_frame.pack(fill = tkinter.X, side = tkinter.BOTTOM)

        label_copyright = ttk.Label(bot_frame, text = 'Copyright (C) 2016 ShadowMan')
        label_copyright.pack(side = tkinter.LEFT, padx = 5, pady = 10)

        label_open_source = ttk.Label(bot_frame, text = 'https://github.com/JShadowMan/bilibili')
        label_open_source.pack(side = tkinter.RIGHT, padx = 5, pady = 10)

        self.live_room_id = entry_value
        self.message = text_value

    def start(self):
        live_room_id = self.live_room_id.get()
        if not live_room_id:
            return

        live_room_id = int(live_room_id)
        helper = Helper.bliHelper(loop = self.__async_loop)
        threading.Thread(target = helper.async_startup,
                                args = (Live.LiveBiliBili(loop = self.__async_loop).listen(live_room_id, MessageHandler),)).start()

    def stop(self):
        pass

    def __init_window_position(self, width, height):
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        x_coordinate = int((screen_width - width) / 2)
        y_coordinate = int((screen_height - height) / 2)

        self.parent.geometry('{}x{}+{}+{}'.format(width, height, x_coordinate, y_coordinate))

if __name__ == '__main__':
    root_window = tkinter.Tk()
    main_frame = GuiApplication(root_window)

    root_window.mainloop()