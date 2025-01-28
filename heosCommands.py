import threading
import telnetlib
import json
import time
from utils import debug_print, set_debug  # Import debug functions
from storage import save_settings  # Import save_settings

debug = True  # Global debug flag

def send_command(ip, command, timeout=10):
    try:
        with telnetlib.Telnet(ip, 1255, timeout) as tn:
            tn.write(command.encode('ascii') + b"\r\n")
            response = tn.read_until(b"\r\n", timeout)
            response_str = response.decode('ascii').strip()
            debug_print(f"Command sent: {command}")
            debug_print(f"Response received: {response_str}")
            return json.loads(response_str)
    except Exception as e:
        debug_print(f"Error sending command to {ip}: {e}")
        return None

def get_player_id(device_ip):
    response = send_command(device_ip, 'heos://player/get_players')
    debug_print(f"Response for get_player_id: {response}")
    if response and 'payload' in response:
        for player in response['payload']:
            if player['ip'] == device_ip:
                debug_print(f"Player ID found: {player['pid']}")
                return player['pid']

    debug_print("Player ID not found")
    return None

def play(device_ip):
    player_id = get_player_id(device_ip)
    debug_print(f"Player ID for play: {player_id}")
    if player_id:
        command = f'heos://player/set_play_state?pid={player_id}&state=play'
        response = send_command(device_ip, command)
        debug_print(f"Response for play: {response}")
        return response
    else:
        debug_print(f"Player ID not found for IP: {device_ip}")
        return None

def stop(device_ip):
    player_id = get_player_id(device_ip)
    debug_print(f"Player ID for stop: {player_id}")
    if player_id:
        command = f'heos://player/set_play_state?pid={player_id}&state=stop'
        response = send_command(device_ip, command)
        debug_print(f"Response for stop: {response}")
        return response
    else:
        debug_print(f"Player ID not found for IP: {device_ip}")
        return None

def set_volume(device_ip, volume_level):
    player_id = get_player_id(device_ip)
    debug_print(f"Player ID for set_volume: {player_id}")
    if player_id:
        command = f'heos://player/set_volume?pid={player_id}&level={volume_level}'
        response = send_command(device_ip, command)
        debug_print(f"Response for set_volume: {response}")
        return response
    else:
        debug_print(f"Player ID not found for IP: {device_ip}")
        return None

def get_state(device_ip):
    player_id = get_player_id(device_ip)
    debug_print(f"Player ID for get_state: {player_id}")
    if player_id:
        command = f'heos://player/get_play_state?pid={player_id}'
        response = send_command(device_ip, command)
        debug_print(f"Response for get_state: {response}")
        if response and 'heos' in response and 'message' in response['heos']:
            # Extract the state from the message
            message = response['heos']['message']
            state = message.split('&')[1].split('=')[1]
            debug_print(f"Extracted state: {state}")
            return state
    else:
        debug_print(f"Player ID not found for IP: {device_ip}")
        return None

def get_players(device_ip):
    response = send_command(device_ip, 'heos://player/get_players')
    debug_print(f"Response for get_players: {response}")
    return response