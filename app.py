import app
from app_components import Menu, Notification, TextDialog
from app_components.tokens import clear_background
import settings

from .config import HEXPANSION_GROUPS
from .slot_settings import (
    get_group_setting,
    set_group_setting,
    get_global_power,
    set_global_power,
    get_global_brightness,
    set_global_brightness,
    get_global_speed,
    set_global_speed,
    get_slot_power,
    set_slot_power,
    copy_slot,
)
from .presets import (
    get_preset_names,
    get_preset_settings,
    save_preset,
    load_preset,
    delete_preset,
    is_builtin_preset,
)
from .effects import Effects
from .menu_builder import build_menu, _POWER_ITEMS, _TYPE_ITEMS, _GROUP_MENU_ITEMS
from .palettes import (
    Palettes,
    save_user_palette,
    delete_user_palette,
    get_user_palette_names,
    get_user_palette_stops,
    preview_user_palette,
)


from tildagonos import tildagonos


class EEHNeoPixelHexpansions(app.App):
    def __init__(self):
        super().__init__()
        self.menu = None
        self.current_menu = None
        self.current_slot = 1
        self.current_group = "Body"
        self.show_palette = False
        self.notification = None
        self.dialog = None
        self.edit_palette_name = None
        self.edit_stop_key = None
        self.preview_palette_name = None
        self.preview_stop_pos = None
        self.pending_action = None
        self.pending_action_back = None
        self.current_preset_name = None
        self.effects = Effects()
        self.palettes = Palettes()
        self.set_menu("main")

    # ---- helpers -----------------------------------------------------------

    def _main_items(self):
        items = ["Power", "Brightness", "Speed", "Palettes"]
        for i in range(1, 7):
            hexp_type = settings.get("drwho.slot.{}".format(i), "None")
            items.append("Slot {}: {}".format(i, hexp_type))
        items.append("About")
        return items

    def _slot_menu_items(self):
        """Return ['Power'] + group names + ['Set Type'] for the current slot."""
        hexp_type = settings.get("drwho.slot.{}".format(self.current_slot), "None")
        items = []
        if hexp_type != "None":
            items.append("Power")
        if hexp_type in HEXPANSION_GROUPS:
            items += ["Area: " + g["name"] for g in HEXPANSION_GROUPS[hexp_type]]
        if hexp_type != "None":
            items.append("Copy From")
        if hexp_type in HEXPANSION_GROUPS:
            items.append("Load Preset")
            items.append("Save Preset")
            all_names = get_preset_names(hexp_type)
            if any(not is_builtin_preset(n, hexp_type) for n in all_names):
                items.append("Delete Preset")
        items.append("Set Type")
        return items

    def _slot_num_from_item(self, item):
        if item.startswith("Slot "):
            try:
                return int(item.split()[1].rstrip(":"))
            except (ValueError, IndexError):
                pass
        return None

    def _current_group_led_count(self):
        hexp_type = settings.get("drwho.slot.{}".format(self.current_slot), "None")
        if hexp_type in HEXPANSION_GROUPS:
            for g in HEXPANSION_GROUPS[hexp_type]:
                if g["name"] == self.current_group:
                    return len(g["leds"])
        return 1

    # ---- navigation --------------------------------------------------------

    def _palette_stop_edit_items(self):
        stops = dict(get_user_palette_stops(self.edit_palette_name))
        colour = stops.get(self.edit_stop_key, (255, 0, 0))
        return [
            "Position: {}".format(self.edit_stop_key),
            "Red: {}".format(colour[0]),
            "Green: {}".format(colour[1]),
            "Blue: {}".format(colour[2]),
            "Delete Stop",
        ]

    def _next_stop_pos(self):
        existing = set(k for k, _ in get_user_palette_stops(self.edit_palette_name))
        for p in range(0, 256, 16):
            if p not in existing:
                return p
        for p in range(256):
            if p not in existing:
                return p
        return 0

    def _on_palette_name_complete(self):
        name = self.dialog.text.strip() if self.dialog else ""
        self.dialog = None
        if name and name not in self.palettes.get_palette_list():
            save_user_palette(name, {0: (255, 0, 0)})
            self.palettes.reload()
            self.edit_palette_name = name
            self.edit_stop_key = 0
            self.set_menu("palette_edit")
        else:
            if name:
                self.notification = Notification("Name taken!")
            self.set_menu("palette_list")

    def _on_palette_name_cancel(self):
        self.dialog = None
        self.set_menu("palette_list")

    def _on_palette_rename_complete(self):
        name = self.dialog.text.strip() if self.dialog else ""
        self.dialog = None
        if not name:
            self.set_menu("palette_edit")
            return
        if name in self.palettes.get_palette_list():
            self.notification = Notification("Name taken!")
            self.set_menu("palette_edit")
            return
        stops = dict(get_user_palette_stops(self.edit_palette_name))
        save_user_palette(name, stops)
        delete_user_palette(self.edit_palette_name)
        self.palettes.reload()
        self.edit_palette_name = name
        self.preview_palette_name = None
        self.show_palette = False
        self.notification = Notification("Renamed!")
        self.set_menu("palette_list")

    def _on_palette_rename_cancel(self):
        self.dialog = None
        self.set_menu("palette_edit")

    def _on_palette_duplicate_complete(self):
        name = self.dialog.text.strip() if self.dialog else ""
        self.dialog = None
        if not name:
            self.set_menu("palette_edit")
            return
        if name in self.palettes.get_palette_list():
            self.notification = Notification("Name taken!")
            self.set_menu("palette_edit")
            return
        stops = dict(get_user_palette_stops(self.edit_palette_name))
        save_user_palette(name, stops)
        self.palettes.reload()
        self.notification = Notification("Duplicated!")
        self.set_menu("palette_edit")

    def _on_palette_duplicate_cancel(self):
        self.dialog = None
        self.set_menu("palette_edit")

    def _on_preset_save_complete(self):
        name = self.dialog.text.strip() if self.dialog else ""
        self.dialog = None
        hexp_type = settings.get("drwho.slot.{}".format(self.current_slot), "None")
        if name and hexp_type in HEXPANSION_GROUPS:
            save_preset(name, hexp_type, self.current_slot)
            self.notification = Notification("Saved!")
        self.set_menu("slot")

    def _on_preset_save_cancel(self):
        self.dialog = None
        self.set_menu("slot")

    def _show_dialog(self, dialog):
        """Show a dialog and kill the current menu's event subscriptions."""
        self.dialog = dialog
        if self.menu:
            self.menu._cleanup()
            self.menu = None

    def _execute_pending_action(self):
        action = self.pending_action
        self.pending_action = None
        if action == "delete_palette":
            delete_user_palette(self.edit_palette_name)
            self.palettes.reload()
            self.edit_palette_name = None
            self.edit_stop_key = None
            self.preview_palette_name = None
            self.show_palette = False
            self.set_menu("palette_list")
        elif action == "delete_preset":
            delete_preset(self.current_preset_name)
            self.current_preset_name = None
            self.set_menu("slot_preset_delete")

    def back_handler(self):
        if self.dialog:
            return
        if self.current_menu == "main":
            self.minimise()
        elif self.current_menu in ("main_power", "main_brightness", "main_speed"):
            if self.current_menu in ("main_brightness", "main_speed"):
                self.effects.clear_global_preview()
            self.set_menu("main")
        elif self.current_menu == "slot":
            self.set_menu("main")
        elif self.current_menu in ("slot_power", "slot_type"):
            self.set_menu("slot")
        elif self.current_menu == "group":
            self.effects.clear_preview(self.current_slot, self.current_group)
            self.show_palette = False
            self.set_menu("slot")
        elif self.current_menu in (
            "group_power",
            "group_speed",
            "group_brightness",
            "group_effect",
            "group_palette",
        ):
            self.effects.clear_preview(self.current_slot, self.current_group)
            self.show_palette = False
            self.set_menu("group")
        elif self.current_menu == "slot_copy":
            self.set_menu("slot")
        elif self.current_menu in (
            "slot_preset_load",
            "slot_preset_delete",
        ):
            if self.current_menu == "slot_preset_load":
                self.effects.clear_preview(self.current_slot)
            self.set_menu("slot")
        elif self.current_menu == "confirm":
            self.pending_action = None
            self.set_menu(self.pending_action_back or "main")
        elif self.current_menu == "palette_list":
            self.show_palette = False
            self.preview_palette_name = None
            self.set_menu("main")
        elif self.current_menu == "palette_edit":
            self.preview_palette_name = None
            self.show_palette = False
            self.set_menu("palette_list")
        elif self.current_menu == "palette_stop_edit":
            self.set_menu("palette_edit")
        elif self.current_menu in (
            "palette_stop_pos",
            "palette_stop_r",
            "palette_stop_g",
            "palette_stop_b",
        ):
            self.palettes.reload()
            self.preview_stop_pos = None
            self.set_menu("palette_stop_edit")
        else:
            self.set_menu("main")

    def select_handler(self, item, idx):
        if self.dialog:
            return
        if self.current_menu == "main":
            if item == "Power":
                self.set_menu("main_power")
            elif item == "Brightness":
                self.set_menu("main_brightness")
            elif item == "Speed":
                self.set_menu("main_speed")
            elif item == "Palettes":
                self.set_menu("palette_list")
            elif item == "About":
                self.set_menu("about")
            else:
                slot_num = self._slot_num_from_item(item)
                if slot_num is not None:
                    self.current_slot = slot_num
                    self.set_menu("slot")

        elif self.current_menu == "main_power":
            if item in _POWER_ITEMS:
                set_global_power(item == "On")
                if item == "Off":
                    self.effects.clear_leds()
                self.notification = Notification("Power {}".format(item))
                self.set_menu("main")

        elif self.current_menu == "main_brightness":
            if item in self.effects.get_brightnesses():
                set_global_brightness(int(item))
                self.effects.clear_global_preview()
                self.notification = Notification("Brightness={}".format(item))
                self.set_menu("main")

        elif self.current_menu == "main_speed":
            if item in self.effects.get_speeds():
                set_global_speed(int(item))
                self.effects.clear_global_preview()
                self.notification = Notification("Speed={}".format(item))
                self.set_menu("main")

        elif self.current_menu == "slot":
            if item == "Power":
                self.set_menu("slot_power")
            elif item == "Copy From":
                self.set_menu("slot_copy")
            elif item == "Set Type":
                self.set_menu("slot_type")
            elif item == "Load Preset":
                self.set_menu("slot_preset_load")
            elif item == "Delete Preset":
                self.set_menu("slot_preset_delete")
            elif item == "Save Preset":
                self._show_dialog(
                    TextDialog(
                        "Preset name?",
                        self,
                        on_complete=self._on_preset_save_complete,
                        on_cancel=self._on_preset_save_cancel,
                    )
                )
            else:
                hexp_type = settings.get(
                    "drwho.slot.{}".format(self.current_slot), "None"
                )
                if hexp_type in HEXPANSION_GROUPS:
                    group_names = [g["name"] for g in HEXPANSION_GROUPS[hexp_type]]
                    name = item[6:] if item.startswith("Area: ") else item
                    if name in group_names:
                        self.current_group = name
                        self.set_menu("group")

        elif self.current_menu == "slot_power":
            if item in _POWER_ITEMS:
                set_slot_power(self.current_slot, item == "On")
                if item == "Off":
                    self.effects.clear_leds()
                self.notification = Notification(
                    "Slot {} {}".format(self.current_slot, item)
                )
                self.set_menu("slot")

        elif self.current_menu == "slot_type":
            if item in _TYPE_ITEMS:
                settings.set("drwho.slot.{}".format(self.current_slot), item)
                settings.save()
                self.effects.clear_leds()
                self.effects.init_chain()
                self.notification = Notification(
                    "Slot {}={}".format(self.current_slot, item)
                )
                self.set_menu("main")

        elif self.current_menu == "group":
            if item == "Power":
                self.set_menu("group_power")
            elif item == "Speed":
                self.set_menu("group_speed")
            elif item == "Brightness":
                self.set_menu("group_brightness")
            elif item == "Effect":
                self.set_menu("group_effect")
            elif item == "Palette":
                self.set_menu("group_palette")

        elif self.current_menu == "group_power":
            if item in _POWER_ITEMS:
                set_group_setting(
                    self.current_slot, self.current_group, "power", item == "On"
                )
                self.effects.clear_preview(self.current_slot, self.current_group)
                self.notification = Notification(
                    "{} {}".format(self.current_group, item)
                )
                self.set_menu("group")

        elif self.current_menu == "group_speed":
            if item in self.effects.get_speeds():
                set_group_setting(
                    self.current_slot, self.current_group, "speed", int(item)
                )
                self.effects.clear_preview(self.current_slot, self.current_group)
                self.notification = Notification("Speed={}".format(item))
                self.set_menu("group")

        elif self.current_menu == "group_brightness":
            if item in self.effects.get_brightnesses():
                set_group_setting(
                    self.current_slot, self.current_group, "brightness", int(item)
                )
                self.effects.clear_preview(self.current_slot, self.current_group)
                self.notification = Notification("Brightness={}".format(item))
                self.set_menu("group")

        elif self.current_menu == "group_effect":
            if item in self.effects.get_effect_list(self._current_group_led_count()):
                set_group_setting(self.current_slot, self.current_group, "effect", item)
                self.effects.clear_preview(self.current_slot, self.current_group)
                self.notification = Notification(item)
                self.set_menu("group")

        elif self.current_menu == "group_palette":
            if item in self.palettes.get_palette_list():
                set_group_setting(
                    self.current_slot, self.current_group, "palette", item
                )
                self.effects.clear_preview(self.current_slot, self.current_group)
                self.show_palette = False
                self.notification = Notification(item)
                self.set_menu("group")

        elif self.current_menu == "slot_copy":
            source = self._slot_num_from_item(item)
            if source is not None:
                copy_slot(source, self.current_slot)
                self.effects.clear_leds()
                self.effects.init_chain()
                self.notification = Notification("Copied Slot {}".format(source))
                self.set_menu("slot")

        elif self.current_menu == "palette_list":
            if item == "New Palette":
                self._show_dialog(
                    TextDialog(
                        "Palette name?",
                        self,
                        on_complete=self._on_palette_name_complete,
                        on_cancel=self._on_palette_name_cancel,
                    )
                )
            else:
                self.edit_palette_name = item
                stops = get_user_palette_stops(item)
                self.edit_stop_key = stops[0][0] if stops else None
                self.set_menu("palette_edit")

        elif self.current_menu == "palette_edit":
            if item == "Add Stop":
                new_pos = self._next_stop_pos()
                existing = dict(get_user_palette_stops(self.edit_palette_name))
                default_colour = (
                    next(iter(existing.values())) if existing else (255, 0, 0)
                )
                existing[new_pos] = default_colour
                save_user_palette(self.edit_palette_name, existing)
                self.palettes.reload()
                self.edit_stop_key = new_pos
                self.set_menu("palette_edit")
            elif item == "Rename":
                self._show_dialog(
                    TextDialog(
                        "New name?",
                        self,
                        on_complete=self._on_palette_rename_complete,
                        on_cancel=self._on_palette_rename_cancel,
                    )
                )
            elif item == "Duplicate":
                self._show_dialog(
                    TextDialog(
                        "Name?",
                        self,
                        on_complete=self._on_palette_duplicate_complete,
                        on_cancel=self._on_palette_duplicate_cancel,
                    )
                )
            elif item == "Delete":
                self.pending_action = "delete_palette"
                self.pending_action_back = "palette_edit"
                self.set_menu("confirm")
            else:
                try:
                    pos = int(item.split()[0].replace("Pos:", ""))
                    self.edit_stop_key = pos
                    self.set_menu("palette_stop_edit")
                except (ValueError, IndexError):
                    pass

        elif self.current_menu == "confirm":
            if item == "Yes - Delete":
                self._execute_pending_action()
            else:
                self.pending_action = None
                self.set_menu(self.pending_action_back or "main")

        elif self.current_menu == "slot_preset_load":
            hexp_type = settings.get("drwho.slot.{}".format(self.current_slot), "None")
            self.effects.clear_preview(self.current_slot)
            load_preset(item, hexp_type, self.current_slot)
            self.effects.clear_leds()
            self.effects.init_chain()
            self.notification = Notification("Loaded!")
            self.set_menu("slot")

        elif self.current_menu == "slot_preset_delete":
            self.current_preset_name = item
            self.pending_action = "delete_preset"
            self.pending_action_back = "slot_preset_delete"
            self.set_menu("confirm")

        elif self.current_menu == "palette_stop_edit":
            if item.startswith("Position"):
                self.set_menu("palette_stop_pos")
            elif item.startswith("Red"):
                self.set_menu("palette_stop_r")
            elif item.startswith("Green"):
                self.set_menu("palette_stop_g")
            elif item.startswith("Blue"):
                self.set_menu("palette_stop_b")
            elif item == "Delete Stop":
                existing = dict(get_user_palette_stops(self.edit_palette_name))
                existing.pop(self.edit_stop_key, None)
                if existing:
                    save_user_palette(self.edit_palette_name, existing)
                    self.palettes.reload()
                    self.edit_stop_key = sorted(existing.keys())[0]
                else:
                    self.notification = Notification("Need >=1 stop")
                self.set_menu("palette_edit")

        elif self.current_menu == "palette_stop_pos":
            new_pos = int(item)
            existing = dict(get_user_palette_stops(self.edit_palette_name))
            src_key = (
                self.preview_stop_pos
                if self.preview_stop_pos is not None
                else self.edit_stop_key
            )
            colour = existing.pop(src_key, (255, 0, 0))
            existing[new_pos] = colour
            save_user_palette(self.edit_palette_name, existing)
            self.palettes.reload()
            self.edit_stop_key = new_pos
            self.preview_stop_pos = None
            self.set_menu("palette_stop_edit")

        elif self.current_menu in (
            "palette_stop_r",
            "palette_stop_g",
            "palette_stop_b",
        ):
            ch = {"palette_stop_r": 0, "palette_stop_g": 1, "palette_stop_b": 2}[
                self.current_menu
            ]
            existing = dict(get_user_palette_stops(self.edit_palette_name))
            colour = list(existing.get(self.edit_stop_key, (255, 0, 0)))
            colour[ch] = int(item)
            existing[self.edit_stop_key] = tuple(colour)
            save_user_palette(self.edit_palette_name, existing)
            self.palettes.reload()
            self.set_menu("palette_stop_edit")

    def change_handler(self, item):
        if self.dialog:
            return
        if self.current_menu == "main_brightness":
            if item in self.effects.get_brightnesses():
                self.effects.set_global_preview("brightness", int(item))
        elif self.current_menu == "main_speed":
            if item in self.effects.get_speeds():
                self.effects.set_global_preview("speed", int(item))
        elif self.current_menu == "group_speed":
            if item in self.effects.get_speeds():
                self.effects.set_preview(
                    self.current_slot, self.current_group, "speed", int(item)
                )
        elif self.current_menu == "group_brightness":
            if item in self.effects.get_brightnesses():
                self.effects.set_preview(
                    self.current_slot, self.current_group, "brightness", int(item)
                )
        elif self.current_menu == "group_effect":
            if item in self.effects.get_effect_list(self._current_group_led_count()):
                self.effects.set_preview(
                    self.current_slot, self.current_group, "effect", item
                )
        elif self.current_menu == "slot_preset_load":
            hexp_type = settings.get("drwho.slot.{}".format(self.current_slot), "None")
            self.effects.clear_preview(self.current_slot)
            preset_data = get_preset_settings(item, hexp_type)
            for group_name, group_data in preset_data.items():
                for key, val in group_data.items():
                    self.effects.set_preview(self.current_slot, group_name, key, val)
        elif self.current_menu == "group_palette":
            self.show_palette = True
            if item in self.palettes.get_palette_list():
                self.effects.set_preview(
                    self.current_slot, self.current_group, "palette", item
                )
        elif self.current_menu in (
            "palette_stop_r",
            "palette_stop_g",
            "palette_stop_b",
        ):
            ch = {"palette_stop_r": 0, "palette_stop_g": 1, "palette_stop_b": 2}[
                self.current_menu
            ]
            existing = dict(get_user_palette_stops(self.edit_palette_name))
            colour = list(existing.get(self.edit_stop_key, (255, 0, 0)))
            try:
                colour[ch] = int(item)
            except (ValueError, TypeError):
                return
            existing[self.edit_stop_key] = tuple(colour)
            preview_user_palette(self.edit_palette_name, existing)
        elif self.current_menu == "palette_list":
            if item != "New Palette":
                self.preview_palette_name = item
                self.show_palette = True
            else:
                self.show_palette = False
                self.preview_palette_name = None
        elif self.current_menu == "palette_edit":
            if item.startswith("Pos:"):
                try:
                    self.preview_stop_pos = int(item.split()[0][4:])
                except (ValueError, IndexError):
                    self.preview_stop_pos = None
            else:
                self.preview_stop_pos = None
        elif self.current_menu == "palette_stop_pos":
            try:
                new_pos = int(item)
            except (ValueError, TypeError):
                return
            existing = dict(get_user_palette_stops(self.edit_palette_name))
            src_key = (
                self.preview_stop_pos
                if self.preview_stop_pos is not None
                else self.edit_stop_key
            )
            if new_pos in existing and new_pos != src_key:
                return
            colour = existing.pop(src_key, (255, 0, 0))
            existing[new_pos] = colour
            preview_user_palette(self.edit_palette_name, existing)
            self.preview_stop_pos = new_pos

    # ---- menu builder ------------------------------------------------------

    def set_menu(self, menu_name):
        if self.menu:
            self.menu._cleanup()
        previous_menu = self.current_menu or "slot"
        self.current_menu = menu_name
        build_menu(self, menu_name, previous_menu)

    # ---- draw / update -----------------------------------------------------

    def draw(self, ctx):
        clear_background(ctx)
        if self.show_palette:
            if self.preview_palette_name:
                shape_colour = self.palettes.get_palette(self.preview_palette_name)
            else:
                shape_colour = self.palettes.get_palette(
                    self.effects.get_palette_name(self.current_slot, self.current_group)
                )
            ctx.linear_gradient(-100, -35, 100, -35)
            for key in sorted(shape_colour.keys()):
                ctx.add_stop(key / 255, shape_colour[key], 1)
            ctx.rectangle(-100, -35, 200, 10).fill()
            if (
                self.current_menu
                in (
                    "palette_edit",
                    "palette_stop_edit",
                    "palette_stop_pos",
                    "palette_stop_r",
                    "palette_stop_g",
                    "palette_stop_b",
                )
                and self.edit_stop_key is not None
            ):
                if self.current_menu == "palette_edit":
                    ind = self.preview_stop_pos
                else:
                    ind = (
                        self.preview_stop_pos
                        if self.preview_stop_pos is not None
                        else self.edit_stop_key
                    )
                if ind is not None:
                    mx = -100 + (ind / 255) * 200
                    ctx.rgb(1, 1, 1).rectangle(mx - 1, -41, 2, 5).fill()

        if self.menu:
            self.menu.draw(ctx)

        if self.notification:
            self.notification.draw(ctx)
        if self.dialog:
            self.dialog.draw(ctx)

    def update(self, delta):
        if self.dialog:
            if hasattr(self.dialog, "update"):
                self.dialog.update(delta)
        else:
            if self.menu:
                self.menu.update(delta)
        if self.notification:
            self.notification.update(delta)

    def background_update(self, delta):
        self.effects.cycle()


__app_export__ = EEHNeoPixelHexpansions
