import threading
import time
import json
import tkinter as tk
from heosCommands import *
from storage import load_settings, save_settings
from utils import debug_print, set_debug
from findDevices import discover_devices
from tkinter import messagebox

debug = True

# Load saved devices into the listbox and return the saved and selected devices
def load_saved_devices(device_listbox, settings):
    saved_devices = settings.get("selected_devices", [])
    selected_devices = []
    for device in saved_devices:
        device_listbox.insert(tk.END, f"{device['name']} ({device['ip']})")
        index = device_listbox.size() - 1
        device_listbox.itemconfig(index, {'bg': '#5e5e5e'})
        device_listbox.select_set(index)
        selected_devices.append(device)
    return saved_devices, selected_devices

# Load saved settings including devices and keep playing state
def load_saved_settings(app):
    app.devices, app.selected_devices = load_saved_devices(app.device_listbox, app.settings)

    app.keep_playing_state = app.settings.get("keep_playing", False)
    app.keep_playing.set(app.keep_playing_state)
    
    if app.keep_playing_state:
        start_keep_playing_thread(app)

# Wrapper function to discover new devices and update the UI
def discover_devices_wrapper(app):
    debug_print("Discovering new devices...")
    discover_devices(app)
    app.discover_button.grid_remove()
    debug_print(f"Selected devices after discovery: {app.selected_devices}")

# Start a thread to discover devices
def start_discover_devices_thread(app):
    app.discover_devices_thread = threading.Thread(target=append_discovered_devices, args=(app, app.devices, app.device_listbox))
    app.discover_devices_thread.daemon = True
    app.discover_devices_thread.start()

# Append newly discovered devices to the listbox without duplicates
def append_discovered_devices(app, devices, device_listbox):
    current_devices = devices.copy()
    discover_devices_wrapper(app)
    new_devices = [device for device in app.devices if device not in current_devices]
    for device in new_devices:
        if not any(device['ip'] in device_listbox.get(i) for i in range(device_listbox.size())):
            app.root.after(0, device_listbox.insert, tk.END, f"{device['name']} ({device['ip']}) - Online")
            app.root.after(0, device_listbox.itemconfig, tk.END, {'bg': '#3e3e3e'})

# Show the Discover button when IP range is changed
def show_discover_button(discover_button, event):
    discover_button.grid()

# Toggle the selection of devices in the listbox and update selected_devices
def toggle_selection(app, event):
    widget = event.widget
    selection = widget.curselection()
    app.selected_devices = []
    for index in selection:
        app.selected_devices.append(app.devices[index])
        widget.itemconfig(index, {'bg': '#5e5e5e'})
    for index in range(widget.size()):
        if index not in selection:
            widget.itemconfig(index, {'bg': '#3e3e3e'})
    save_selected_settings(app)

# Save the selected settings including keep playing state and selected devices
def save_selected_settings(app):
    app.settings["keep_playing"] = app.keep_playing.get()
    app.settings["selected_devices"] = app.selected_devices
    save_settings(app.settings)

# Save the selected devices based on their background color in the listbox
def save_selected_devices(app):
    app.selected_devices = [app.devices[i] for i in range(app.device_listbox.size()) if app.device_listbox.itemcget(i, 'bg') == '#5e5e5e']
    app.settings["selected_devices"] = app.selected_devices

# Play the selected devices
def play_selected_devices(selected_devices):
    print(selected_devices)
    debug_print("Playing selected devices...")
    for device in selected_devices:
        play(device['ip'])

# Stop the selected devices
def stop_selected_devices(selected_devices):
    debug_print("Stopping selected devices...")
    for device in selected_devices:
        debug_print(f"Sending stop command to {device['name']} ({device['ip']})")
        stop(device['ip'])

# Toggle the keep playing state and start/stop the keep playing thread
def toggle_keep_playing(app):
    app.settings["keep_playing"] = app.keep_playing.get()
    save_settings(app.settings)
    if app.keep_playing.get():
        start_keep_playing_thread(app)
    else:
        stop_keep_playing_thread(app.keep_playing)

# Start the keep playing thread
def start_keep_playing_thread(app):
    keep_playing_thread = threading.Thread(target=keep_playing_function, args=(app.keep_playing, app.selected_devices))
    keep_playing_thread.daemon = True
    keep_playing_thread.start()

# Stop the keep playing thread
def stop_keep_playing_thread(keep_playing):
    keep_playing.set(False)

# Function to keep playing the selected devices at intervals
def keep_playing_function(keep_playing, selected_devices):
    while keep_playing.get():
        play_selected_devices(selected_devices)
        time.sleep(10)