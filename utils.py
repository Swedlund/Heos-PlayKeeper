debug = False  # Global debug flag

def set_debug(value):
    global debug
    debug = value

def debug_print(message):
    if debug:
        print(message)