# Hardware constants and hexpansion type/group definitions.
# No imports from our own modules — safe to import anywhere.

SKIP_LED = 0  # LEDs to skip at chain start (non-zero for Sim testing)
FPS_LIMIT = 20

# Slot number → GPIO pin
_pin_mapping = {
    1: 39,
    2: 35,
    3: 34,
    4: 11,
    5: 18,
    6: 3,
}

# Per-group setting defaults
_DEFAULTS = {
    "power": True,
    "speed": 5,
    "brightness": 50,
    "effect": "Flash",
    "palette": "Red",
}

# Hexpansion types: name → total LED count
HEXPANSION_TYPES = {
    "EEH Logo": 14,  # H
    "Dalek": 3,  # eye, ear left, ear right
    "K9": 1,  # eye
    "Sonic Screwdriver": 1,  # tip
    "TARDIS": 5,  # window ×4, beacon
}

# Named LED groups per hexpansion type
HEXPANSION_GROUPS = {
    "EEH Logo": [
        {"name": "Main", "leds": list(range(14))},
    ],
    "Dalek": [
        {"name": "Ears", "leds": [0, 1]},
        {"name": "Eye", "leds": [2]},
    ],
    "K9": [
        {"name": "Eyes", "leds": [0]},
    ],
    "Sonic Screwdriver": [
        {"name": "Tip", "leds": [0]},
    ],
    "TARDIS": [
        {"name": "Beacon", "leds": [4]},
        {"name": "Windows", "leds": [1, 0, 3, 2]},
    ],
}
