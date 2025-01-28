import tkinter as tk
from scapy import all as scapy
from storage import save_settings
from heosCommands import get_players
from tkinter import messagebox
from utils import debug_print

def get_network_devices(ip_range):
    # Create an ARP request packet
    arp = scapy.ARP(pdst=ip_range)
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = scapy.srp(packet, timeout=3, verbose=0)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

def filter_denon_heos_devices(devices):
    # Denon HEOS MAC address prefixes (example prefixes, please verify the actual ones)
    denon_heos_prefixes = ["00:05:CD", "00:1E:7C", "00:1F:3A"]

    # Filter devices with MAC addresses starting with Denon HEOS prefixes
    heos_devices = [device for device in devices if any(device['mac'].lower().startswith(prefix.lower()) for prefix in denon_heos_prefixes)]
    
    return heos_devices

def discover_devices(app):
    ip_range = app.ip_range_entry.get()
    if ip_range:
        # Save the IP range to settings
        app.settings["ip_range"] = ip_range
        save_settings(app.settings)
        
        added_ips = set(device['ip'] for device in app.devices)  # Track already added IPs
        discovered_devices = get_network_devices(ip_range)
        heos_devices = filter_denon_heos_devices(discovered_devices)
        for device in heos_devices:
            device_ip = device['ip']
            if device_ip not in added_ips:
                player_info = get_players(device_ip)
                if player_info and 'payload' in player_info:
                    for player in player_info['payload']:
                        if player['ip'] not in added_ips:
                            app.device_listbox.insert(tk.END, f"{player['name']} ({player['ip']})")
                            app.devices.append(player)
                            added_ips.add(player['ip'])
    else:
        messagebox.showwarning("Input Error", "Please enter the IP range.")