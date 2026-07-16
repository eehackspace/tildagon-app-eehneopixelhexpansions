import time
import random
import neopixel
from machine import Pin
import settings

from .config import (
    HEXPANSION_TYPES,
    HEXPANSION_GROUPS,
    SKIP_LED,
    FPS_LIMIT,
    _pin_mapping,
)
from .slot_settings import (
    get_group_setting,
    get_slot_power,
    get_global_power,
    get_global_brightness,
    get_global_speed,
)
from .palettes import get_palette as _palette_get

# SOS morse pattern: (on=1/off=0, duration_in_units) pairs
_SOS_SEQ = (
    (1, 1),
    (0, 1),
    (1, 1),
    (0, 1),
    (1, 1),
    (0, 3),  # S
    (1, 3),
    (0, 1),
    (1, 3),
    (0, 1),
    (1, 3),
    (0, 3),  # O
    (1, 1),
    (0, 1),
    (1, 1),
    (0, 1),
    (1, 1),
    (0, 7),  # S
)
_SOS_UNIT_FRAMES = 5  # frames per dot unit


class Effects:
    def __init__(self):
        self._effect_defs = [
            ("Breathe", 1),
            ("Candle", 1),
            ("Chatter", 1),
            ("Colour Chase", 2),
            ("Colour Cycle", 1),
            ("Comet", 2),
            ("Fire", 1),
            ("Flash", 1),
            ("Heartbeat", 1),
            ("Scanner", 2),
            ("Solid", 1),
            ("SOS", 1),
            ("Strobe", 1),
            ("Twinkle", 1),
        ]
        self.effect_list = [name for name, _ in self._effect_defs]
        # (effect_name, min_leds) — effects with min_leds > 1 are hidden for single-LED groups
        # (slot_num, group_name, key) -> preview value
        self._previews = {}
        # "brightness" | "speed" -> global preview value
        self._global_previews = {}
        self.last_cycle_time = time.ticks_ms()
        self.chains = []
        self.init_chain()

    def init_chain(self):
        """Build NeoPixel chains with per-group LED ranges from slot config."""
        self.chains = []
        for slot_num in range(1, 7):
            hexp_type = settings.get("drwho.slot.{}".format(slot_num), "None")
            if hexp_type not in HEXPANSION_GROUPS:
                continue
            led_count = HEXPANSION_TYPES[hexp_type]
            np = neopixel.NeoPixel(Pin(_pin_mapping[slot_num]), led_count + SKIP_LED)
            groups = []
            for g in HEXPANSION_GROUPS[hexp_type]:
                groups.append(
                    {
                        "name": g["name"],
                        "leds": g["leds"],
                        "current_cycle": 0,
                        "candle_brightness": 0.5,
                        "candle_target": 0.5,
                        "sos_step": 0,
                        "sos_frame": 0,
                    }
                )
            self.chains.append(
                {
                    "np": np,
                    "slot_num": slot_num,
                    "groups": groups,
                }
            )

    # ---- per-group setting helpers -----------------------------------------

    def _get(self, slot_num, group_name, key):
        """Return preview value if active, otherwise the persisted setting."""
        v = self._previews.get((slot_num, group_name, key))
        return v if v is not None else get_group_setting(slot_num, group_name, key)

    def set_preview(self, slot_num, group_name, key, value):
        if value is None:
            self._previews.pop((slot_num, group_name, key), None)
        else:
            self._previews[(slot_num, group_name, key)] = value

    def clear_preview(self, slot_num, group_name=None):
        for k in list(self._previews):
            if k[0] == slot_num and (group_name is None or k[1] == group_name):
                del self._previews[k]

    # ---- global preview helpers --------------------------------------------

    def set_global_preview(self, key, value):
        self._global_previews[key] = value

    def clear_global_preview(self):
        self._global_previews.clear()

    def _get_global(self, key):
        if key in self._global_previews:
            return self._global_previews[key]
        if key == "brightness":
            return get_global_brightness()
        return get_global_speed()

    def get_speed(self, slot_num, group_name):
        return int(self._get(slot_num, group_name, "speed"))

    def get_brightness(self, slot_num, group_name):
        return int(self._get(slot_num, group_name, "brightness"))

    def get_effect(self, slot_num, group_name):
        effect = self._get(slot_num, group_name, "effect")
        return effect if effect in self.effect_list else "Flash"

    def get_palette_name(self, slot_num, group_name):
        name = self._get(slot_num, group_name, "palette")
        return name if name else "Red"

    def get_palette(self, slot_num, group_name):
        return _palette_get(self.get_palette_name(slot_num, group_name))

    def _first_colour(self, palette):
        """Return the first non-black colour in the palette (sorted by key)."""
        for k in sorted(palette.keys()):
            c = palette[k]
            if c != (0, 0, 0):
                return c
        return palette[sorted(palette.keys())[0]]

    def _interp_palette(self, palette, pos):
        """Linearly interpolate palette at position pos (0–255)."""
        keys = sorted(palette.keys())
        if pos <= keys[0]:
            return palette[keys[0]]
        if pos >= keys[-1]:
            return palette[keys[-1]]
        for i in range(len(keys) - 1):
            if keys[i] <= pos <= keys[i + 1]:
                t = (pos - keys[i]) / (keys[i + 1] - keys[i])
                c1, c2 = palette[keys[i]], palette[keys[i + 1]]
                return (
                    int(c1[0] + (c2[0] - c1[0]) * t),
                    int(c1[1] + (c2[1] - c1[1]) * t),
                    int(c1[2] + (c2[2] - c1[2]) * t),
                )
        return palette[keys[-1]]

    def get_power(self, slot_num, group_name):
        return bool(self._get(slot_num, group_name, "power"))

    def get_speeds(self):
        return [str(s) for s in range(1, 11)]

    def get_brightnesses(self):
        return [str(b) for b in range(5, 101, 5)]

    def get_effect_list(self, led_count=1):
        return [name for name, min_leds in self._effect_defs if led_count >= min_leds]

    # ---- cycling -----------------------------------------------------------

    def cycle(self):
        current_time = time.ticks_ms()
        if current_time - self.last_cycle_time >= (1000 / FPS_LIMIT):
            if not get_global_power():
                self.clear_leds()
            else:
                for chain_info in self.chains:
                    self._cycle_chain(chain_info)
            self.last_cycle_time = current_time

    def _cycle_chain(self, chain_info):
        """Drive each group on this chain independently, then write once."""
        slot_num = chain_info["slot_num"]
        np = chain_info["np"]
        if not get_slot_power(slot_num):
            for group_info in chain_info["groups"]:
                for led_idx in group_info["leds"]:
                    np[led_idx + SKIP_LED] = (0, 0, 0)
            np.write()
            return
        for group_info in chain_info["groups"]:
            group_name = group_info["name"]
            if not self.get_power(slot_num, group_name):
                for led_idx in group_info["leds"]:
                    np[led_idx + SKIP_LED] = (0, 0, 0)
                continue
            gs = self._get_global("speed")
            group_speed = self.get_speed(slot_num, group_name)
            effective_speed = min(10, round(group_speed * gs / 5)) if gs > 0 else 0
            group_info["current_cycle"] = (
                group_info["current_cycle"] + effective_speed
            ) % 256
            effect = self.get_effect(slot_num, group_name)
            method_name = "_fx_" + effect.lower().replace(" ", "_")
            getattr(self, method_name, self._fx_chatter)(chain_info, group_info)
        np.write()

    # ---- LED helpers -------------------------------------------------------

    def _write_led(self, chain_info, group_info, led_idx, color, brightness=1.0):
        mb = (self._get_global("brightness") / 100) * (
            self.get_brightness(chain_info["slot_num"], group_info["name"]) / 100
        )
        r = int(color[0] * brightness * mb)
        g = int(color[1] * brightness * mb)
        b = int(color[2] * brightness * mb)
        chain_info["np"][led_idx + SKIP_LED] = (r, g, b)

    def _write_group(self, chain_info, group_info, color, brightness=1.0):
        for led_idx in group_info["leds"]:
            self._write_led(chain_info, group_info, led_idx, color, brightness)

    def _clear_group(self, chain_info, group_info):
        for led_idx in group_info["leds"]:
            chain_info["np"][led_idx + SKIP_LED] = (0, 0, 0)

    def clear_leds(self):
        for chain_info in self.chains:
            np = chain_info["np"]
            for group_info in chain_info["groups"]:
                for led_idx in group_info["leds"]:
                    np[led_idx + SKIP_LED] = (0, 0, 0)
            np.write()

    # ---- effect methods (per group) ----------------------------------------

    def _fx_flash(self, chain_info, group_info):
        colour = self._first_colour(
            self.get_palette(chain_info["slot_num"], group_info["name"])
        )
        if group_info["current_cycle"] % 32 < 16:
            self._write_group(chain_info, group_info, colour)
        else:
            self._clear_group(chain_info, group_info)

    def _fx_breathe(self, chain_info, group_info):
        colour = self._first_colour(
            self.get_palette(chain_info["slot_num"], group_info["name"])
        )
        t = group_info["current_cycle"] / 255.0
        brightness = t * 2 if t < 0.5 else (1.0 - t) * 2
        self._write_group(chain_info, group_info, colour, brightness)

    def _fx_chatter(self, chain_info, group_info):
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        colour = self._first_colour(self.get_palette(slot_num, group_name))
        speak_probability = self.get_speed(slot_num, group_name) / 10.0 * 0.8
        brightness = (
            random.uniform(0.3, 1.0) if random.random() < speak_probability else 0.05
        )
        self._write_group(chain_info, group_info, colour, brightness)

    def _fx_colour_cycle(self, chain_info, group_info):
        palette = self.get_palette(chain_info["slot_num"], group_info["name"])
        phase = (group_info["current_cycle"] * 2) % 512
        pos = phase if phase < 256 else 511 - phase
        self._write_group(chain_info, group_info, self._interp_palette(palette, pos))

    def _fx_colour_chase(self, chain_info, group_info):
        palette = self.get_palette(chain_info["slot_num"], group_info["name"])
        num_leds = len(group_info["leds"])
        step = 256 // num_leds if num_leds > 1 else 0
        for i, led_idx in enumerate(group_info["leds"]):
            pos = (group_info["current_cycle"] + i * step) % 256
            self._write_led(
                chain_info, group_info, led_idx, self._interp_palette(palette, pos)
            )

    def _fx_heartbeat(self, chain_info, group_info):
        colour = self._first_colour(
            self.get_palette(chain_info["slot_num"], group_info["name"])
        )
        t = group_info["current_cycle"] % 64
        if t < 8:
            brightness = t / 8.0
        elif t < 16:
            brightness = (16 - t) / 8.0
        elif t < 24:
            brightness = 0.6 * (t - 16) / 8.0
        elif t < 32:
            brightness = 0.6 * (32 - t) / 8.0
        else:
            brightness = 0.0
        self._write_group(chain_info, group_info, colour, brightness)

    def _fx_solid(self, chain_info, group_info):
        self._write_group(
            chain_info,
            group_info,
            self._first_colour(
                self.get_palette(chain_info["slot_num"], group_info["name"])
            ),
        )

    def _fx_sos(self, chain_info, group_info):
        colour = self._first_colour(
            self.get_palette(chain_info["slot_num"], group_info["name"])
        )
        state, _ = _SOS_SEQ[group_info["sos_step"]]
        if state:
            self._write_group(chain_info, group_info, colour)
        else:
            self._clear_group(chain_info, group_info)
        group_info["sos_frame"] += 1
        if (
            group_info["sos_frame"]
            >= _SOS_SEQ[group_info["sos_step"]][1] * _SOS_UNIT_FRAMES
        ):
            group_info["sos_frame"] = 0
            group_info["sos_step"] = (group_info["sos_step"] + 1) % len(_SOS_SEQ)

    def _fx_candle(self, chain_info, group_info):
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        colour = self._first_colour(self.get_palette(slot_num, group_name))
        flicker_rate = self.get_speed(slot_num, group_name) / 10.0
        if random.random() < 0.2 + flicker_rate * 0.4:
            group_info["candle_target"] = random.uniform(0.05, 1.0)
        lerp = 0.15 + flicker_rate * 0.4
        group_info["candle_brightness"] += (
            group_info["candle_target"] - group_info["candle_brightness"]
        ) * lerp
        self._write_group(
            chain_info, group_info, colour, group_info["candle_brightness"]
        )

    def _fx_strobe(self, chain_info, group_info):
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        palette = self.get_palette(slot_num, group_name)
        keys = sorted(palette.keys())
        n = len(keys)
        segments = n if n > 1 else 2
        speed = self.get_speed(slot_num, group_name)
        gs = max(1, self._get_global("speed"))
        # speed 1 = 10 frames/phase at neutral global (gs=5); global speed scales it
        half_period = max(1, (11 - speed) * 5 // gs)
        if "strobe_frame" not in group_info:
            group_info["strobe_frame"] = 0
        phase = (group_info["strobe_frame"] // half_period) % segments
        group_info["strobe_frame"] += 1
        if n == 1 and phase >= 1:
            self._clear_group(chain_info, group_info)
        else:
            self._write_group(chain_info, group_info, palette[keys[phase % n]])

    def _fx_twinkle(self, chain_info, group_info):
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        colour = self._first_colour(self.get_palette(slot_num, group_name))
        speed = self.get_speed(slot_num, group_name)
        sparkle_chance = (speed + 1) / 120.0
        decay = 0.04 + speed * 0.008
        if "twinkle" not in group_info:
            group_info["twinkle"] = [0.0] * len(group_info["leds"])
        brs = group_info["twinkle"]
        for i, led_idx in enumerate(group_info["leds"]):
            if brs[i] < 0.05 and random.random() < sparkle_chance:
                brs[i] = random.uniform(0.7, 1.0)
            else:
                brs[i] = max(0.0, brs[i] - decay)
            self._write_led(chain_info, group_info, led_idx, colour, brs[i])

    def _fx_scanner(self, chain_info, group_info):
        """Larson scanner: bright head bounces back and forth with fading trail."""
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        colour = self._first_colour(self.get_palette(slot_num, group_name))
        speed = self.get_speed(slot_num, group_name)
        gs = max(1, self._get_global("speed"))
        n = len(group_info["leds"])
        if "scanner_pos" not in group_info:
            group_info["scanner_pos"] = 0.0
            group_info["scanner_dir"] = 1
        step = n * speed * gs / 1000.0
        group_info["scanner_pos"] += group_info["scanner_dir"] * step
        if group_info["scanner_pos"] >= n - 1:
            group_info["scanner_pos"] = float(n - 1)
            group_info["scanner_dir"] = -1
        elif group_info["scanner_pos"] <= 0.0:
            group_info["scanner_pos"] = 0.0
            group_info["scanner_dir"] = 1
        head = group_info["scanner_pos"]
        for i, led_idx in enumerate(group_info["leds"]):
            brightness = max(0.0, 1.0 - abs(i - head) * 0.55)
            self._write_led(chain_info, group_info, led_idx, colour, brightness)

    def _fx_comet(self, chain_info, group_info):
        """Comet: bright head loops around chain with a decaying tail."""
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        colour = self._first_colour(self.get_palette(slot_num, group_name))
        speed = self.get_speed(slot_num, group_name)
        gs = max(1, self._get_global("speed"))
        n = len(group_info["leds"])
        if "comet_brs" not in group_info:
            group_info["comet_brs"] = [0.0] * n
            group_info["comet_pos"] = 0.0
        step = n * speed * gs / 1000.0
        group_info["comet_pos"] = (group_info["comet_pos"] + step) % n
        decay = 0.10 + speed * 0.018
        brs = group_info["comet_brs"]
        for i in range(n):
            brs[i] = max(0.0, brs[i] - decay)
        brs[int(group_info["comet_pos"])] = 1.0
        for i, led_idx in enumerate(group_info["leds"]):
            self._write_led(chain_info, group_info, led_idx, colour, brs[i])

    def _fx_fire(self, chain_info, group_info):
        """Fire: independent per-LED heat simulation mapped through the palette."""
        slot_num = chain_info["slot_num"]
        group_name = group_info["name"]
        palette = self.get_palette(slot_num, group_name)
        keys = sorted(palette.keys())
        speed = self.get_speed(slot_num, group_name)
        n = len(group_info["leds"])
        if "fire_heat" not in group_info:
            group_info["fire_heat"] = [random.uniform(0.5, 1.0) for _ in range(n)]
        heat = group_info["fire_heat"]
        rate = 0.12 + speed * 0.025
        for i in range(n):
            heat[i] += random.uniform(-rate, rate * 0.6)
            heat[i] = max(0.05, min(1.0, heat[i]))
        for i, led_idx in enumerate(group_info["leds"]):
            self._write_led(
                chain_info,
                group_info,
                led_idx,
                self._interp_palette(palette, heat[i] * keys[-1]),
            )
