import re

from enum import IntFlag

mods_regex = re.compile(r'(?i)[-+~|]?(?:EZ|HD|HR|DT|HT|NC|FL|TD)+[~|]?')
mods_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'AU', 'SO', 'AP', 'PF',
             'K4', 'K5', 'K6', 'K7', 'K8', 'KM', 'FI', 'RD', 'LM', 'K9', 'KX', 'K1', 'K3', 'K2', 'V2']


def stringify_mods(mods_enabled):
    mods = [name for index, name in enumerate(mods_list) if 1 << index & mods_enabled]
    if "NC" in mods:
        mods.remove("DT")
    return "".join(mods)


def modsify_string(mod_string):
    mod_string = mod_string.strip("-+~|").upper()
    return sum([1 << mods_list.index(mod_string[i:i + 2]) for i in range(0, len(mod_string), 2)])


def has_mod(mods_enabled, mod):
    return mods_enabled & mod == mod


class ModFlag(IntFlag):
    NF = NoFail         = 1
    EZ = Easy           = 2
    TD = TouchDevice    = 4
    HD = Hidden         = 8
    HR = HardRock       = 16
    SD = SuddenDeath    = 32
    DT = DoubleTime     = 64
    RX = Relax          = 128
    HT = HalfTime       = 256
    NC = Nightcore      = 512   # Only set along with DoubleTime. i.e: NC only gives 576
    FL = Flashlight     = 1024
    AU = Autoplay       = 2048
    SO = SpunOut        = 4096
    AP = Relax2         = 8192  # Autopilot
    PF = Perfect        = 16384 # Only set along with SuddenDeath. i.e: PF only gives 16416
    K4 = Key4           = 32768
    K5 = Key5           = 65536
    K6 = Key6           = 131072
    K7 = Key7           = 262144
    K8 = Key8           = 524288
    FI = FadeIn         = 1048576
    RD = Random         = 2097152
    Cinema         = 4194304
    Target         = 8388608
    K9 = Key9           = 16777216
    KX = KeyCoop        = 33554432
    K1 = Key1           = 67108864
    K3 = Key3           = 134217728
    K2 = Key2           = 268435456
    V2 = ScoreV2        = 536870912
    Mirror         = 1073741824
