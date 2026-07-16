import settings

from .config import HEXPANSION_GROUPS, _DEFAULTS


def get_group_setting(slot_num, group_name, key):
    return settings.get(
        "drwho.slot.{}.{}.{}".format(slot_num, group_name, key), _DEFAULTS[key]
    )


def set_group_setting(slot_num, group_name, key, value):
    settings.set("drwho.slot.{}.{}.{}".format(slot_num, group_name, key), value)
    settings.save()


def get_global_power():
    return bool(settings.get("drwho.global.power", True))


def set_global_power(value):
    settings.set("drwho.global.power", value)
    settings.save()


def get_slot_power(slot_num):
    return bool(settings.get("drwho.slot.{}.power".format(slot_num), True))


def set_slot_power(slot_num, value):
    settings.set("drwho.slot.{}.power".format(slot_num), value)
    settings.save()


def get_global_brightness():
    # 100 = no change; 0 = fully dark
    return int(settings.get("drwho.global.brightness", 100))


def set_global_brightness(value):
    settings.set("drwho.global.brightness", value)
    settings.save()


def get_global_speed():
    # 5 = neutral (1×); 0 = frozen; 10 ≈ 2× faster
    return int(settings.get("drwho.global.speed", 5))


def set_global_speed(value):
    settings.set("drwho.global.speed", value)
    settings.save()


def copy_slot(source_slot, dest_slot):
    src_type = settings.get("drwho.slot.{}".format(source_slot), "None")
    settings.set("drwho.slot.{}".format(dest_slot), src_type)
    if src_type in HEXPANSION_GROUPS:
        for g in HEXPANSION_GROUPS[src_type]:
            group_name = g["name"]
            for key in _DEFAULTS:
                val = get_group_setting(source_slot, group_name, key)
                settings.set(
                    "drwho.slot.{}.{}.{}".format(dest_slot, group_name, key), val
                )
    settings.save()
