import settings

from .config import HEXPANSION_GROUPS, _DEFAULTS
from .slot_settings import get_group_setting

# Built-in default presets per hexpansion type
_DEFAULT_PRESETS = {
    "EEH Logo": {
        "Default": {
            "Main": {
                "effect": "Colour Chase",
                "palette": "Rainbow",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Fire": {
            "Main": {
                "effect": "Fire",
                "palette": "Red",
                "speed": 6,
                "brightness": 100,
                "power": True,
            },
        },
        "Chill": {
            "Main": {
                "effect": "Breathe",
                "palette": "Cyan",
                "speed": 3,
                "brightness": 60,
                "power": True,
            },
        },
        "Twinkle": {
            "Main": {
                "effect": "Twinkle",
                "palette": "RGBY",
                "speed": 5,
                "brightness": 80,
                "power": True,
            },
        },
        "Comet": {
            "Main": {
                "effect": "Comet",
                "palette": "Rainbow",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "EMF": {
            "Main": {
                "effect": "Colour Chase",
                "palette": "EMF2026",
                "speed": 6,
                "brightness": 100,
                "power": True,
            },
        },
        "Heartbeat": {
            "Main": {
                "effect": "Heartbeat",
                "palette": "Red",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Rainbow Cycle": {
            "Main": {
                "effect": "Colour Cycle",
                "palette": "Rainbow",
                "speed": 4,
                "brightness": 80,
                "power": True,
            },
        },
        "Lava": {
            "Main": {
                "effect": "Fire",
                "palette": "Orange",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "Ocean": {
            "Main": {
                "effect": "Comet",
                "palette": "Cyan",
                "speed": 5,
                "brightness": 80,
                "power": True,
            },
        },
    },
    "Dalek": {
        "Default": {
            "Ears": {
                "effect": "Chatter",
                "palette": "White",
                "speed": 7,
                "brightness": 80,
                "power": True,
            },
            "Eye": {
                "effect": "Breathe",
                "palette": "Blue",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "Angry": {
            "Ears": {
                "effect": "Flash",
                "palette": "Blink Red",
                "speed": 9,
                "brightness": 100,
                "power": True,
            },
            "Eye": {
                "effect": "Flash",
                "palette": "Blink Red",
                "speed": 7,
                "brightness": 80,
                "power": True,
            },
        },
        "Exterminate": {
            "Ears": {
                "effect": "Strobe",
                "palette": "Blink Red",
                "speed": 9,
                "brightness": 100,
                "power": True,
            },
            "Eye": {
                "effect": "Strobe",
                "palette": "Aqua Flash",
                "speed": 9,
                "brightness": 100,
                "power": True,
            },
        },
        "Speaking": {
            "Ears": {
                "effect": "Chatter",
                "palette": "Warm White",
                "speed": 6,
                "brightness": 90,
                "power": True,
            },
            "Eye": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Idle": {
            "Ears": {
                "effect": "Solid",
                "palette": "White",
                "speed": 5,
                "brightness": 20,
                "power": True,
            },
            "Eye": {
                "effect": "Breathe",
                "palette": "Blue",
                "speed": 2,
                "brightness": 40,
                "power": True,
            },
        },
        "Acquire Target": {
            "Ears": {
                "effect": "Scanner",
                "palette": "Blue Cyan Yellow",
                "speed": 6,
                "brightness": 80,
                "power": True,
            },
            "Eye": {
                "effect": "Flash",
                "palette": "Red",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "Patrol": {
            "Ears": {
                "effect": "Scanner",
                "palette": "White",
                "speed": 5,
                "brightness": 60,
                "power": True,
            },
            "Eye": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 5,
                "brightness": 80,
                "power": True,
            },
        },
        "Listening": {
            "Ears": {
                "effect": "Breathe",
                "palette": "White",
                "speed": 3,
                "brightness": 40,
                "power": True,
            },
            "Eye": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Dormant": {
            "Ears": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 1,
                "brightness": 10,
                "power": True,
            },
            "Eye": {
                "effect": "Breathe",
                "palette": "April Night",
                "speed": 1,
                "brightness": 20,
                "power": True,
            },
        },
        "Stealth": {
            "Ears": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 1,
                "brightness": 15,
                "power": True,
            },
            "Eye": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 1,
                "brightness": 25,
                "power": True,
            },
        },
    },
    "K9": {
        "Default": {
            "Eyes": {
                "effect": "Chatter",
                "palette": "Red",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Standby": {
            "Eyes": {
                "effect": "Breathe",
                "palette": "Red",
                "speed": 2,
                "brightness": 30,
                "power": True,
            },
        },
        "Alert": {
            "Eyes": {
                "effect": "Flash",
                "palette": "Blink Red",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "Happy": {
            "Eyes": {
                "effect": "Heartbeat",
                "palette": "Red",
                "speed": 4,
                "brightness": 100,
                "power": True,
            },
        },
        "Thinking": {
            "Eyes": {
                "effect": "Breathe",
                "palette": "Yellow",
                "speed": 2,
                "brightness": 60,
                "power": True,
            },
        },
        "Danger": {
            "Eyes": {
                "effect": "Strobe",
                "palette": "Blink Red",
                "speed": 8,
                "brightness": 100,
                "power": True,
            },
        },
        "Offline": {
            "Eyes": {
                "effect": "Solid",
                "palette": "Warm White",
                "speed": 1,
                "brightness": 10,
                "power": True,
            },
        },
        "Computing": {
            "Eyes": {
                "effect": "Twinkle",
                "palette": "Blue Cyan Yellow",
                "speed": 4,
                "brightness": 70,
                "power": True,
            },
        },
        "Awaiting Orders": {
            "Eyes": {
                "effect": "Solid",
                "palette": "Red",
                "speed": 1,
                "brightness": 45,
                "power": True,
            },
        },
        "Scanning": {
            "Eyes": {
                "effect": "Flash",
                "palette": "Aqua Flash",
                "speed": 5,
                "brightness": 90,
                "power": True,
            },
        },
    },
    "Sonic Screwdriver": {
        "Default": {
            "Tip": {
                "effect": "Breathe",
                "palette": "Green",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
        },
        "Active": {
            "Tip": {
                "effect": "Strobe",
                "palette": "Cyan",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
        },
        "Scanning": {
            "Tip": {
                "effect": "Flash",
                "palette": "Aqua Flash",
                "speed": 8,
                "brightness": 80,
                "power": True,
            },
        },
        "Overloaded": {
            "Tip": {
                "effect": "Strobe",
                "palette": "White",
                "speed": 9,
                "brightness": 100,
                "power": True,
            },
        },
        "Idle": {
            "Tip": {
                "effect": "Solid",
                "palette": "Green",
                "speed": 1,
                "brightness": 30,
                "power": True,
            },
        },
        "Locked": {
            "Tip": {
                "effect": "Flash",
                "palette": "Red",
                "speed": 6,
                "brightness": 100,
                "power": True,
            },
        },
        "Hacking": {
            "Tip": {
                "effect": "Colour Cycle",
                "palette": "Aurora",
                "speed": 6,
                "brightness": 100,
                "power": True,
            },
        },
        "Interference": {
            "Tip": {
                "effect": "Strobe",
                "palette": "Blue Magenta",
                "speed": 5,
                "brightness": 90,
                "power": True,
            },
        },
        "Diagnostics": {
            "Tip": {
                "effect": "Heartbeat",
                "palette": "Blue Cyan Yellow",
                "speed": 5,
                "brightness": 90,
                "power": True,
            },
        },
        "Deadlock": {
            "Tip": {
                "effect": "Solid",
                "palette": "Red",
                "speed": 1,
                "brightness": 100,
                "power": True,
            },
        },
    },
    "TARDIS": {
        "Default": {
            "Beacon": {
                "effect": "Breathe",
                "palette": "White",
                "speed": 6,
                "brightness": 80,
                "power": True,
            },
            "Windows": {
                "effect": "Candle",
                "palette": "Warm White",
                "speed": 3,
                "brightness": 50,
                "power": True,
            },
        },
        "Emergency": {
            "Beacon": {
                "effect": "Strobe",
                "palette": "Blink Red",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
            "Windows": {
                "effect": "Scanner",
                "palette": "Blink Red",
                "speed": 4,
                "brightness": 30,
                "power": True,
            },
        },
        "Landed": {
            "Beacon": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 1,
                "brightness": 30,
                "power": True,
            },
            "Windows": {
                "effect": "Candle",
                "palette": "Warm White",
                "speed": 2,
                "brightness": 30,
                "power": True,
            },
        },
        "Materialising": {
            "Beacon": {
                "effect": "Colour Cycle",
                "palette": "Cyan",
                "speed": 7,
                "brightness": 100,
                "power": True,
            },
            "Windows": {
                "effect": "Twinkle",
                "palette": "Warm White",
                "speed": 5,
                "brightness": 80,
                "power": True,
            },
        },
        "Night": {
            "Beacon": {
                "effect": "Breathe",
                "palette": "April Night",
                "speed": 2,
                "brightness": 20,
                "power": True,
            },
            "Windows": {
                "effect": "Candle",
                "palette": "Warm White",
                "speed": 1,
                "brightness": 20,
                "power": True,
            },
        },
        "Distress": {
            "Beacon": {
                "effect": "SOS",
                "palette": "White",
                "speed": 5,
                "brightness": 100,
                "power": True,
            },
            "Windows": {
                "effect": "Flash",
                "palette": "Blink Red",
                "speed": 4,
                "brightness": 50,
                "power": True,
            },
        },
        "Time Vortex": {
            "Beacon": {
                "effect": "Colour Cycle",
                "palette": "Blue Magenta",
                "speed": 6,
                "brightness": 100,
                "power": True,
            },
            "Windows": {
                "effect": "Colour Chase",
                "palette": "Atlantica",
                "speed": 5,
                "brightness": 70,
                "power": True,
            },
        },
        "Cloaked": {
            "Beacon": {
                "effect": "Solid",
                "palette": "Blue",
                "speed": 1,
                "brightness": 10,
                "power": True,
            },
            "Windows": {
                "effect": "Solid",
                "palette": "Warm White",
                "speed": 1,
                "brightness": 10,
                "power": True,
            },
        },
        "Interior Lights": {
            "Beacon": {
                "effect": "Solid",
                "palette": "Warm White",
                "speed": 1,
                "brightness": 25,
                "power": True,
            },
            "Windows": {
                "effect": "Candle",
                "palette": "Warm White",
                "speed": 2,
                "brightness": 40,
                "power": True,
            },
        },
        "Takeoff": {
            "Beacon": {
                "effect": "Strobe",
                "palette": "Blue Magenta",
                "speed": 8,
                "brightness": 100,
                "power": True,
            },
            "Windows": {
                "effect": "Colour Cycle",
                "palette": "Aurora",
                "speed": 6,
                "brightness": 90,
                "power": True,
            },
        },
    },
}


def get_preset_settings(name, hexp_type):
    """Return {group_name: {key: value}} for a preset without applying it."""
    if hexp_type not in HEXPANSION_GROUPS:
        return {}
    builtin = _DEFAULT_PRESETS.get(hexp_type, {}).get(name)
    result = {}
    if builtin:
        for g in HEXPANSION_GROUPS[hexp_type]:
            group_name = g["name"]
            if group_name in builtin:
                result[group_name] = dict(builtin[group_name])
    else:
        for g in HEXPANSION_GROUPS[hexp_type]:
            group_name = g["name"]
            result[group_name] = {
                key: settings.get(
                    "drwho.preset.{}.{}.{}".format(name, group_name, key),
                    _DEFAULTS[key],
                )
                for key in _DEFAULTS
            }
    return result


def is_builtin_preset(name, hexp_type):
    return name in _DEFAULT_PRESETS.get(hexp_type, {})


def get_preset_names(hexp_type):
    """Return built-in + user preset names for a given hexpansion type."""
    builtin = list(_DEFAULT_PRESETS.get(hexp_type, {}).keys())
    raw = settings.get("drwho.preset.names", "")
    user = [
        n
        for n in raw.split(",")
        if n and settings.get("drwho.preset.{}.type".format(n), "") == hexp_type
    ]
    all_names = sorted(builtin + user)
    if "Default" in all_names:
        all_names.remove("Default")
        all_names.insert(0, "Default")
    return all_names


def save_preset(name, hexp_type, slot_num):
    """Save current slot group settings as a user preset."""
    if hexp_type not in HEXPANSION_GROUPS:
        return
    settings.set("drwho.preset.{}.type".format(name), hexp_type)
    for g in HEXPANSION_GROUPS[hexp_type]:
        group_name = g["name"]
        for key in _DEFAULTS:
            val = get_group_setting(slot_num, group_name, key)
            settings.set("drwho.preset.{}.{}.{}".format(name, group_name, key), val)
    raw = settings.get("drwho.preset.names", "")
    names = [n for n in raw.split(",") if n]
    if name not in names:
        names.append(name)
        settings.set("drwho.preset.names", ",".join(names))
    settings.save()


def load_preset(name, hexp_type, slot_num):
    """Apply a built-in or user preset to a slot."""
    if hexp_type not in HEXPANSION_GROUPS:
        return
    builtin = _DEFAULT_PRESETS.get(hexp_type, {}).get(name)
    if builtin:
        for g in HEXPANSION_GROUPS[hexp_type]:
            group_name = g["name"]
            if group_name in builtin:
                for key, val in builtin[group_name].items():
                    settings.set(
                        "drwho.slot.{}.{}.{}".format(slot_num, group_name, key), val
                    )
        settings.save()
        return
    for g in HEXPANSION_GROUPS[hexp_type]:
        group_name = g["name"]
        for key in _DEFAULTS:
            val = settings.get(
                "drwho.preset.{}.{}.{}".format(name, group_name, key), _DEFAULTS[key]
            )
            settings.set("drwho.slot.{}.{}.{}".format(slot_num, group_name, key), val)
    settings.save()


def delete_preset(name):
    """Delete a user preset."""
    raw = settings.get("drwho.preset.names", "")
    names = [n for n in raw.split(",") if n and n != name]
    settings.set("drwho.preset.names", ",".join(names))
    settings.save()
