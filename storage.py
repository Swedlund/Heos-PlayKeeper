import json

def save_settings(settings, filename="settings.txt"):
    with open(filename, "w") as file:
        json.dump(settings, file, indent=4)

def load_settings(filename="settings.txt"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}