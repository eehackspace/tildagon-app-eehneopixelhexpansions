import settings

from app_components import Menu, Notification

from .config import HEXPANSION_TYPES, HEXPANSION_GROUPS
from .slot_settings import (
    get_global_power,
    get_global_brightness,
    get_global_speed,
    get_slot_power,
    get_group_setting,
)
from .presets import get_preset_names, is_builtin_preset, get_preset_settings
from .palettes import get_user_palette_names, get_user_palette_stops

_GROUP_MENU_ITEMS = ["Power", "Speed", "Brightness", "Effect", "Palette"]
_POWER_ITEMS = ["On", "Off"]
_TYPE_ITEMS = ["None"] + sorted(HEXPANSION_TYPES.keys())


def build_menu(a, menu_name, previous_menu):
    if menu_name == "main":
        items = a._main_items()
        # Power=0, Brightness=1, Speed=2, Palettes=3, Slot 1-6 at 4-9, About=10
        pos = a.current_slot + 3  # slot N → index N+3
        if pos < 4 or pos >= len(items):
            pos = 4
        if previous_menu == "about":
            pos = len(items) - 1
        elif previous_menu == "main_power":
            pos = 0
        elif previous_menu == "main_brightness":
            pos = 1
        elif previous_menu == "main_speed":
            pos = 2
        elif previous_menu == "palette_list":
            pos = 3
        a.menu = Menu(
            a,
            items,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "slot":
        items = a._slot_menu_items()
        sub_map = {
            "slot_power": "Power",
            "slot_copy": "Copy From",
            "slot_type": "Set Type",
            "slot_preset_load": "Load Preset",
            "slot_preset_delete": "Delete Preset",
            "group": "Area: " + a.current_group,
        }
        label = sub_map.get(previous_menu)
        if label is not None and label in items:
            pos = items.index(label)
        else:
            pos = 0
        a.menu = Menu(
            a,
            items,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "main_power":
        a.menu = Menu(
            a,
            _POWER_ITEMS,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=0 if get_global_power() else 1,
        )

    elif menu_name == "main_brightness":
        brightnesses = a.effects.get_brightnesses()
        try:
            pos = brightnesses.index(str(get_global_brightness()))
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            brightnesses,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "main_speed":
        speeds = a.effects.get_speeds()
        try:
            pos = speeds.index(str(get_global_speed()))
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            speeds,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "slot_power":
        a.menu = Menu(
            a,
            _POWER_ITEMS,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=0 if get_slot_power(a.current_slot) else 1,
        )

    elif menu_name == "slot_type":
        hexp_type = settings.get("drwho.slot.{}".format(a.current_slot), "None")
        try:
            pos = _TYPE_ITEMS.index(hexp_type)
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            _TYPE_ITEMS,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "group":
        sub_map = {
            "group_power": "Power",
            "group_speed": "Speed",
            "group_brightness": "Brightness",
            "group_effect": "Effect",
            "group_palette": "Palette",
        }
        try:
            pos = _GROUP_MENU_ITEMS.index(sub_map.get(previous_menu, "Power"))
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            _GROUP_MENU_ITEMS,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "group_power":
        power = get_group_setting(a.current_slot, a.current_group, "power")
        a.menu = Menu(
            a,
            _POWER_ITEMS,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=0 if power else 1,
        )

    elif menu_name == "group_speed":
        speeds = a.effects.get_speeds()
        try:
            pos = speeds.index(
                str(a.effects.get_speed(a.current_slot, a.current_group))
            )
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            speeds,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "group_brightness":
        brightnesses = a.effects.get_brightnesses()
        try:
            pos = brightnesses.index(
                str(a.effects.get_brightness(a.current_slot, a.current_group))
            )
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            brightnesses,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "group_effect":
        effect_list = a.effects.get_effect_list(a._current_group_led_count())
        try:
            pos = effect_list.index(
                a.effects.get_effect(a.current_slot, a.current_group)
            )
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            effect_list,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "group_palette":
        a.show_palette = True
        palette_list = a.palettes.get_palette_list()
        try:
            pos = palette_list.index(
                a.effects.get_palette_name(a.current_slot, a.current_group)
            )
        except ValueError:
            pos = 0
        a.menu = Menu(
            a,
            palette_list,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos,
        )

    elif menu_name == "slot_copy":
        items = []
        for i in range(1, 7):
            if i != a.current_slot:
                t = settings.get("drwho.slot.{}".format(i), "None")
                items.append("Slot {}: {}".format(i, t))
        a.menu = Menu(
            a,
            items,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
        )

    elif menu_name == "slot_preset_load":
        hexp_type = settings.get("drwho.slot.{}".format(a.current_slot), "None")
        all_names = get_preset_names(hexp_type)
        if not all_names:
            a.notification = Notification("No presets!")
            a.set_menu("slot")
            return
        preset_data = get_preset_settings(all_names[0], hexp_type)
        a.effects.clear_preview(a.current_slot)
        for group_name, group_data in preset_data.items():
            for key, val in group_data.items():
                a.effects.set_preview(a.current_slot, group_name, key, val)
        a.menu = Menu(
            a,
            list(all_names),
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
        )

    elif menu_name == "slot_preset_delete":
        hexp_type = settings.get("drwho.slot.{}".format(a.current_slot), "None")
        all_names = get_preset_names(hexp_type)
        user_names = [n for n in all_names if not is_builtin_preset(n, hexp_type)]
        if not user_names:
            a.notification = Notification("No user presets!")
            a.set_menu("slot")
            return
        a.menu = Menu(
            a,
            user_names,
            select_handler=a.select_handler,
            back_handler=a.back_handler,
        )

    elif menu_name == "confirm":
        a.menu = Menu(
            a,
            ["Yes - Delete", "Cancel"],
            select_handler=a.select_handler,
            back_handler=a.back_handler,
        )

    elif menu_name == "palette_list":
        user_names = get_user_palette_names()
        items = user_names + ["New Palette"]
        if user_names:
            a.preview_palette_name = user_names[0]
            a.show_palette = True
        else:
            a.show_palette = False
            a.preview_palette_name = None
        a.menu = Menu(
            a,
            items,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
        )

    elif menu_name == "palette_edit":
        a.show_palette = True
        a.preview_palette_name = a.edit_palette_name
        a.preview_stop_pos = a.edit_stop_key
        items = []
        for pos, (r, g, b) in get_user_palette_stops(a.edit_palette_name):
            items.append("Pos:{} R:{} G:{} B:{}".format(pos, r, g, b))
        items += ["Add Stop", "Rename", "Duplicate", "Delete Palette"]
        stop_idx = 0
        if a.edit_stop_key is not None:
            for idx, (p, _) in enumerate(get_user_palette_stops(a.edit_palette_name)):
                if p == a.edit_stop_key:
                    stop_idx = idx
                    break
        a.menu = Menu(
            a,
            items,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=stop_idx,
        )

    elif menu_name == "palette_stop_edit":
        a.preview_stop_pos = None
        sub_map = {
            "palette_stop_pos": 0,
            "palette_stop_r": 1,
            "palette_stop_g": 2,
            "palette_stop_b": 3,
        }
        pos_idx = sub_map.get(previous_menu, 0)
        a.menu = Menu(
            a,
            a._palette_stop_edit_items(),
            select_handler=a.select_handler,
            back_handler=a.back_handler,
            position=pos_idx,
        )

    elif menu_name == "palette_stop_pos":
        a.show_palette = True
        a.preview_palette_name = a.edit_palette_name
        a.preview_stop_pos = None
        occupied = set(k for k, _ in get_user_palette_stops(a.edit_palette_name))
        occupied.discard(a.edit_stop_key)
        positions = [
            str(i) for i in list(range(0, 256, 16)) + [255] if i not in occupied
        ]
        try:
            pos_idx = positions.index(str(a.edit_stop_key))
        except ValueError:
            pos_idx = 0
        a.menu = Menu(
            a,
            positions,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos_idx,
        )

    elif menu_name in ("palette_stop_r", "palette_stop_g", "palette_stop_b"):
        a.show_palette = True
        a.preview_palette_name = a.edit_palette_name
        values = [str(i) for i in range(0, 256, 5)]
        stops = dict(get_user_palette_stops(a.edit_palette_name))
        colour = stops.get(a.edit_stop_key, (255, 0, 0))
        ch = {"palette_stop_r": 0, "palette_stop_g": 1, "palette_stop_b": 2}[menu_name]
        rounded = (colour[ch] // 5) * 5
        try:
            pos_idx = values.index(str(rounded))
        except ValueError:
            pos_idx = 0
        a.menu = Menu(
            a,
            values,
            select_handler=a.select_handler,
            change_handler=a.change_handler,
            back_handler=a.back_handler,
            position=pos_idx,
        )

    elif menu_name == "about":
        a.menu = Menu(
            a,
            [
                "Version: 0.1.0",
                "",
                "Essex Hackspace",
                "Neopixel Hexpansions",
                "EEH Logo / Dalek / K9",
                "Sonic Screwdriver / Tardis",
                "eehack.space",
                "",
                "Available at",
                "EMF 2026 at",
                "the East Essex",
                "Hackspace village!",
            ],
            back_handler=a.back_handler,
        )
