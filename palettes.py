import settings

from .palette_data import palettes

_FEATURED_PALETTES = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Cyan",
    "Blue",
    "Purple",
    "Magenta",
    "Pink",
    "White",
    "Warm White",
    "Rainbow",
    "RGB",
    "RGBY",
    "EMF2026",
    "EMF2024",
]


_user_palettes = {}


def _load_user_palettes():
    global _user_palettes
    _user_palettes = {}
    names_raw = settings.get("drwho.palette.user.names", "")
    for name in [n for n in names_raw.split(",") if n]:
        raw = settings.get("drwho.palette.user.{}".format(name), "")
        d = {}
        for stop in raw.split(";"):
            parts = stop.split(",")
            if len(parts) == 4:
                try:
                    d[int(parts[0])] = (int(parts[1]), int(parts[2]), int(parts[3]))
                except ValueError:
                    pass
        if d:
            _user_palettes[name] = d


def save_user_palette(name, stops_dict):
    _user_palettes[name] = stops_dict
    settings.set(
        "drwho.palette.user.{}".format(name),
        ";".join(
            "{},{},{},{}".format(pos, r, g, b)
            for pos, (r, g, b) in sorted(stops_dict.items())
        ),
    )
    names = get_user_palette_names()
    if name not in names:
        names.append(name)
        settings.set("drwho.palette.user.names", ",".join(names))
    settings.save()


def delete_user_palette(name):
    _user_palettes.pop(name, None)
    settings.set("drwho.palette.user.{}".format(name), "")
    names = [n for n in get_user_palette_names() if n != name]
    settings.set("drwho.palette.user.names", ",".join(names))
    settings.save()


def get_user_palette_names():
    raw = settings.get("drwho.palette.user.names", "")
    return [n for n in raw.split(",") if n]


def get_user_palette_stops(name):
    return sorted(_user_palettes.get(name, {}).items())


def preview_user_palette(name, stops_dict):
    """Update _user_palettes in-memory without saving to settings."""
    if name:
        _user_palettes[name] = stops_dict


def get_palette(name):
    if name in palettes:
        return palettes[name]
    if name in _user_palettes:
        return _user_palettes[name]
    return palettes["Red"]


class Palettes:
    def __init__(self):

        self.palette = settings.get("drwho.palette", "Red")
        self.preview_palette = None

        _load_user_palettes()
        featured = [p for p in _FEATURED_PALETTES if p in palettes]
        rest = sorted(p for p in palettes if p not in _FEATURED_PALETTES)
        self.palette_list = featured + rest + get_user_palette_names()

    def get_palette_list(self):
        return self.palette_list

    def get_palette(self, palette):
        return get_palette(palette)

    def reload(self):
        _load_user_palettes()
        featured = [p for p in _FEATURED_PALETTES if p in palettes]
        rest = sorted(p for p in palettes if p not in _FEATURED_PALETTES)
        self.palette_list = featured + rest + get_user_palette_names()
