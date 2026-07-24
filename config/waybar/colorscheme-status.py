#!/usr/bin/env python3
import json
import os

STATE_FILE = os.path.expanduser("~/.local/state/colorscheme")

try:
    with open(STATE_FILE) as f:
        scheme = f.read().strip()
except FileNotFoundError:
    scheme = "dark"

if scheme == "light":
    print(json.dumps({
        "text": "☀",
        "tooltip": "Fargetema: lyst\nToggle: Super+Alt+A",
        "class": "light"
    }))
else:
    print(json.dumps({
        "text": "☾",
        "tooltip": "Fargetema: mørkt\nToggle: Super+Alt+A",
        "class": "dark"
    }))
