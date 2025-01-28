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
        
        # Construct the path to the icon file
        icon_path = fetch_resource("icon/icon.ico")
        
        # Load the icon using Pillow and convert it to a format that tk.PhotoImage can recognize
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.root.iconphoto(False, icon_photo)
        
        self.debug = debug
        set_debug(self.debug)
        self.devices = []
        self.selected_devices = []
        self.keep_playing = tk.BooleanVar()
        self.selection_state = {}

        # Load settings
        self.settings = load_settings()
        
        # Create and place the IP range label and entry
        tk.Label(root, text="IP Range:", bg="#2e2e2e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10)
        self.ip_range_entry = tk.Entry(root, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        self.ip_range_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.ip_range_entry.bind("<KeyRelease>", lambda event: show_discover_button(self.discover_button, event))

        # Set the IP range entry with the last used IP range or default
        last_ip_range = self.settings.get("ip_range", "192.168.1.1/24")
        self.ip_range_entry.insert(0, last_ip_range)

        # Create and place the Discover button
        self.discover_button = tk.Button(root, text="Discover", command=lambda: discover_devices_wrapper(self), bg="#4e4e4e", fg="#ffffff")
        self.discover_button.grid(row=0, column=2, padx=10, pady=10)
        self.discover_button.grid_remove()  # Hide the button initially

        # Create and place the device listbox
        self.device_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, bg="#3e3e3e", fg="#ffffff", selectbackground="#5e5e5e", selectforeground="#ffffff")
        self.device_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.device_listbox.bind('<ButtonRelease-1>', lambda event: toggle_selection(self, event))

        # Create and place the Play and Stop buttons
        self.stop_button = tk.Button(root, text="Stop", command=lambda: stop_selected_devices(self.selected_devices), bg="#4e4e4e", fg="#ffffff")
        self.stop_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.play_button = tk.Button(root, text="Play", command=lambda: play_selected_devices(self.selected_devices), bg="#4e4e4e", fg="#ffffff")
        self.play_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Create and place the Keep Playing checkbox
        self.keep_playing_checkbox = tk.Checkbutton(root, text="Keep playing", variable=self.keep_playing, bg="#2e2e2e", fg="#ffffff", selectcolor="#2e2e2e", command=lambda: toggle_keep_playing(self))
        self.keep_playing_checkbox.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Configure grid to make the listbox expand with the window
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # Load saved settings
        load_saved_settings(self)
        
        # Discover devices on app start in a separate thread
        start_discover_devices_thread(self)

def main():
    root = tk.Tk()
    app = HeosApp(root, debug=False)
    root.mainloop()

if __name__ == "__main__":
    main()