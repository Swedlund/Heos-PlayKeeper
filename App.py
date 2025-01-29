import os
import sys
import tkinter as tk
from PIL import ImageTk, Image
import threading
import time
from tkinter import messagebox
from deviceManager import *
from storage import load_settings
from utils import set_debug, debug_print
import pystray
from pystray import MenuItem as item

def fetch_resource(rsrc_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        return rsrc_path
    else:
        return os.path.join(base_path, rsrc_path)

class HeosApp:
    def __init__(self, root, debug=False):
        self.root = root
        self.root.title("Heos PlayKeeper")
        self.root.configure(bg="#2e2e2e")
        self.root.minsize(250, 300)
        
        icon_path = fetch_resource("images/icon/icon.ico")
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(False, icon_photo)
        
        self.debug = debug
        set_debug(self.debug)
        self.devices = []
        self.selected_devices = []
        self.keep_playing = tk.BooleanVar()
        self.app_minimized = tk.BooleanVar()
        self.selection_state = {}

        # Load settings
        self.settings = load_settings()
        
        # IP range label and entry
        tk.Label(root, text="IP Range:", bg="#2e2e2e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ip_range_entry = tk.Entry(root, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        self.ip_range_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="e")
        self.ip_range_entry.bind("<KeyRelease>", lambda event: show_discover_button(self.discover_button, event))
        last_ip_range = self.settings.get("ip_range", "192.168.1.1/24")
        self.ip_range_entry.insert(0, last_ip_range)

        # Discover button
        self.discover_button = tk.Button(root, text="Discover", command=lambda: discover_devices_wrapper(self), bg="#4e4e4e", fg="#ffffff")
        self.discover_button.grid(row=0, column=5, padx=10, pady=10)
        self.discover_button.grid_remove()  # Hide the button initially

        # Device listbox
        self.device_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, bg="#3e3e3e", fg="#ffffff", selectbackground="#5e5e5e", selectforeground="#ffffff")
        self.device_listbox.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")
        self.device_listbox.bind('<ButtonRelease-1>', lambda event: toggle_selection(self, event))

        # Play and Stop buttons
        button_frame = tk.Frame(root, bg="#2e2e2e")
        button_frame.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="w")
        self.stop_button = tk.Button(button_frame, text="Stop", command=lambda: stop_selected_devices(self.selected_devices), bg="#4e4e4e", fg="#ffffff")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        self.play_button = tk.Button(button_frame, text="Play", command=lambda: play_selected_devices(self.selected_devices), bg="#4e4e4e", fg="#ffffff")
        self.play_button.pack(side=tk.LEFT)

        # Keep Playing checkbox
        self.keep_playing_checkbox = tk.Checkbutton(root, text="Keep playing", variable=self.keep_playing, bg="#2e2e2e", fg="#ffffff", selectcolor="#2e2e2e", command=lambda: toggle_keep_playing(self))
        self.keep_playing_checkbox.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        # Minimized to tray on start checkbox
        self.minimized_checkbox = tk.Checkbutton(root, text="Minimized to tray on start", variable=self.app_minimized, bg="#2e2e2e", fg="#ffffff", selectcolor="#2e2e2e", command=lambda: save_selected_settings(self))
        self.minimized_checkbox.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")

        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=3)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

        root.grid_rowconfigure(1, weight=1)

        # Load saved settings
        load_saved_settings(self)
        
        # Discover devices on app start in a separate thread
        start_discover_devices_thread(self)

        # Minimize to tray if the setting is enabled
        if self.app_minimized.get():
            self.root.withdraw()
            self.create_tray_icon()

        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_tray_icon(self):
        icon_path = fetch_resource("images/icon/icon.ico")
        image = Image.open(icon_path)

        menu = (item('Show', self.show_window), item('Quit', self.quit_app))
        self.tray_icon = pystray.Icon("Heos PlayKeeper", image, "Heos PlayKeeper", menu)
        self.tray_icon.run_detached()

    def show_window(self, icon, item):
        self.root.deiconify()
        self.tray_icon.stop()

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.quit()

    def on_closing(self):
        save_selected_settings(self)
        self.root.withdraw()
        self.create_tray_icon()

def main():
    root = tk.Tk()
    app = HeosApp(root, debug=False)
    root.mainloop()

if __name__ == "__main__":
    main()