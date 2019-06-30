import re

mods_regex = re.compile(r'(?:EZ|HD|HR|DT|HT|NC|FL)+')


class RecommendationCriteria:
    __slots__ = ["user", "mods", "notmods", "max_creation_date", "max_length", "max_combo", "max_ar", "max_od", "max_cs",
                 "max_bpm", "min_creation_date", "min_length", "min_combo", "min_ar", "min_od", "min_cs", "min_bpm",
                 "targets"]

    def __init__(self, user, mods=0, notmods=0, max_creation_date=0, max_length=0, max_combo=0, max_ar=0, max_od=0, max_cs=0,
                 max_bpm=0, min_creation_date=0, min_length=0, min_combo=0, min_ar=0, min_od=0, min_cs=0, min_bpm=0):
        self.user = user
        self.mods = mods
        self.notmods = notmods
        self.max_creation_date = max_creation_date
        self.max_length = max_length
        self.max_combo = max_combo
        self.max_ar = max_ar
        self.max_od = max_od
        self.max_cs = max_cs
        self.max_bpm = max_bpm
        self.min_creation_date = min_creation_date
        self.min_length = min_length
        self.min_combo = min_combo
        self.min_ar = min_ar
        self.min_od = min_od
        self.min_cs = min_cs
        self.min_bpm = min_bpm
        self.targets = None


mods_list = ['NF', 'EZ', 'TD', 'HD', 'HR', 'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'AU', 'SO', 'AP', 'PF',
             'K4', 'K5', 'K6', 'K7', 'K8', 'KM', 'FI', 'RD', 'LM', 'K9', 'KX', 'K1', 'K3', 'K2', 'V2']


def stringify_mods(mods_enabled):
    mods = [name for index, name in enumerate(mods_list) if 2 ** index & mods_enabled]
    if "NC" in mods:
        mods.remove("DT")
    return "".join(mods)


def modsify_string(mod_string):
    return sum([2 ** mods_list.index(mod_string[i:i + 2]) for i in range(0, len(mod_string), 2)])


def parse_criteria(user, message):
    criteria = RecommendationCriteria(user)
    objects = message.split(" ")
    second_object_is_mods = False

    # first object is always !r or !recommend, as we've tested the command against a regex before

    if len(objects) < 2:
        return criteria

    for object in objects[1:]:
        if not any(x in object for x in "<>="):
            if object.upper() == "NOMOD":
                criteria.mods = -1
            elif object.upper().startswith('NOT:') and mods_regex.match(object.upper()[4:]):
                criteria.notmods = modsify_string(object.upper()[4:])
                if criteria.notmods & 512:
                    criteria.notmods |= 64
            elif mods_regex.match(object.upper()):
                criteria.mods = modsify_string(object.upper())
                if criteria.mods & 512:
                    criteria.mods |= 64

        for x in ("<=", ">=", "<", ">", "="):
            if x not in object:
                continue

            parts = object.split(x)

            if parts[0] not in ("creation_date", "length", "combo", "ar", "od", "cs", "bpm"):
                break

            if x == "<=":
                setattr(criteria, "max_%s" % parts[0], parts[1])
            elif x == ">=":
                setattr(criteria, "min_%s" % parts[0], parts[1])
            elif x == "<":
                setattr(criteria, "max_%s" % parts[0], float(parts[1]) - 0.01)
            elif x == ">":
                setattr(criteria, "min_%s" % parts[0], float(parts[1]) + 0.01)
            elif x == "=":
                setattr(criteria, "max_%s" % parts[0], parts[1])
                setattr(criteria, "min_%s" % parts[0], parts[1])

            break

    return criteria
