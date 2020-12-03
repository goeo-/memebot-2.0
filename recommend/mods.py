import re

from enum import IntFlag

mods_regex = re.compile(r'(?:EZ|HD|HR|DT|HT|NC|FL|TD)+')
mods_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'AU', 'SO', 'AP', 'PF',
             'K4', 'K5', 'K6', 'K7', 'K8', 'KM', 'FI', 'RD', 'LM', 'K9', 'KX', 'K1', 'K3', 'K2', 'V2']


def stringify_mods(mods_enabled):
    mods = [name for index, name in enumerate(mods_list) if 2 ** index & mods_enabled]
    if "NC" in mods:
        mods.remove("DT")
    return "".join(mods)


def modsify_string(mod_string):
    return sum([2 ** mods_list.index(mod_string[i:i + 2]) for i in range(0, len(mod_string), 2)])


def has_mod(mods_enabled, mod):
    return mods_enabled & mod == mod


class ModFlag(IntFlag):
    NoFail         = 1
    Easy           = 2
    TouchDevice    = 4
    Hidden         = 8
    HardRock       = 16
    SuddenDeath    = 32
    DoubleTime     = 64
    Relax          = 128
    HalfTime       = 256
    Nightcore      = 512   # Only set along with DoubleTime. i.e: NC only gives 576
    Flashlight     = 1024
    Autoplay       = 2048
    SpunOut        = 4096
    Relax2         = 8192  # Autopilot
    Perfect        = 16384 # Only set along with SuddenDeath. i.e: PF only gives 16416  
    Key4           = 32768
    Key5           = 65536
    Key6           = 131072
    Key7           = 262144
    Key8           = 524288
    FadeIn         = 1048576
    Random         = 2097152
    Cinema         = 4194304
    Target         = 8388608
    Key9           = 16777216
    KeyCoop        = 33554432
    Key1           = 67108864
    Key3           = 134217728
    Key2           = 268435456
    ScoreV2        = 536870912
    Mirror         = 1073741824
