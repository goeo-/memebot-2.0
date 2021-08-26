from datetime import datetime
from recommend.mods import modsify_string, mods_regex
from recommend.maps import InvalidDateException, InvalidNumberException

date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m", "%Y/%m", "%Y"]

class RecommendationCriteria:
    __slots__ = ["user", "mods", "notmods", "max_creation_date", "max_length", "max_combo", "max_star", "max_ar",
                 "max_od", "max_cs", "max_hp", "max_bpm", "min_creation_date", "min_length", "min_combo", "min_star",
                 "min_ar", "min_od", "min_cs", "min_hp", "min_bpm", "targets"]

    def __init__(self, user, mods=0, notmods=0, max_creation_date=0, max_length=0, max_combo=0, max_star=0, max_ar=0,
                 max_od=0, max_cs=0, max_hp=0, max_bpm=0, min_creation_date=0, min_length=0, min_combo=0, min_star=0,
                 min_ar=0, min_od=0, min_cs=0, min_hp=0, min_bpm=0):
        self.user = user
        self.mods = mods
        self.notmods = notmods
        self.max_creation_date = max_creation_date
        self.max_length = max_length
        self.max_combo = max_combo
        self.max_star = max_star
        self.max_ar = max_ar
        self.max_od = max_od
        self.max_cs = max_cs
        self.max_hp = max_hp
        self.max_bpm = max_bpm
        self.min_creation_date = min_creation_date
        self.min_length = min_length
        self.min_combo = min_combo
        self.min_star = min_star
        self.min_ar = min_ar
        self.min_od = min_od
        self.min_cs = min_cs
        self.min_hp = min_hp
        self.min_bpm = min_bpm
        self.targets = None


def parse_date(filter):
    for format in date_formats: # try to find a matching date format
        try:
            return datetime.strptime(filter, format)
        except ValueError:
            continue

    raise InvalidDateException


def parse_criteria(user, message):
    criteria = RecommendationCriteria(user)
    objects = message.split(" ")

    # first object is always !r or !recommend, as we've tested the command against a regex before

    if len(objects) < 2:
        return criteria

    for obj in objects[1:]:
        if not any(x in obj for x in "<>="):
            if obj.upper() == "NOMOD":
                criteria.mods = -1
            elif obj.upper().startswith('NOT:') and mods_regex.fullmatch(obj[4:]):
                criteria.notmods = modsify_string(obj.upper()[4:])
            elif mods_regex.fullmatch(obj):
                criteria.mods = modsify_string(obj)

        for x in ("<=", ">=", "<", ">", "="):
            if x not in obj:
                continue

            parts = obj.lower().split(x)

            if parts[0] not in ("creation_date", "created", "date", "length", "len", "combo", "sr", "stars", "star", "ar", "od", "cs", "hp", "bpm"):
                break

            # aliases
            if parts[0] in ("created", "date"):
                parts[0] = "creation_date"
            elif parts[0] == "len":
                parts[0] = "length"
            elif parts[0] in ("sr", "stars"):
                parts[0] = "star"

            if parts[0] == "creation_date":
                value = parse_date(parts[1])
            else:
                if parts[1].replace('.', '', 1).isdecimal():
                    value = float(parts[1])
                else:
                    raise InvalidNumberException

            if x == "<=":
                setattr(criteria, "max_%s" % parts[0], value)
            elif x == ">=":
                setattr(criteria, "min_%s" % parts[0], value)
            elif x == "<":
                setattr(criteria, "max_%s" % parts[0], (value - 0.01) if type(value) == "float" else value)
            elif x == ">":
                setattr(criteria, "min_%s" % parts[0], (value + 0.01) if type(value) == "float" else value)
            elif x == "=":
                setattr(criteria, "max_%s" % parts[0], value)
                setattr(criteria, "min_%s" % parts[0], value)

            break

    return criteria
