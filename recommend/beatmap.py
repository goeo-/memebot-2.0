from time import strftime, gmtime

from recommend.mods import stringify_mods, has_mod, ModFlag
from singletons.osu_api import OsuAPI

def time_for_mods(time, mods_enabled):
    if has_mod(mods_enabled, ModFlag.DoubleTime):
        return int(time * 0.75)
    return time


def bpm_for_mods(bpm, mods_enabled):
    if has_mod(mods_enabled, ModFlag.DoubleTime):
        return int(bpm * 1.5)
    else:
        return int(bpm)
        

async def get_beatmap_by_id(beatmap_id):
    beatmap = await OsuAPI().call("get_beatmaps", {"b": beatmap_id, "m": 0})

    try:
        return beatmap[0]
    except (KeyError, IndexError):
        print('Had an issue with map:', beatmap_id)
        return None


class Beatmap:
    def __init__(self, beatmap_id, beatmap, enabled_mods, stars, ar, od, combo=None):
        self.beatmap_id = beatmap_id
        self.beatmap = beatmap
        self.enabled_mods = enabled_mods
        self.stars = stars
        self.ar = ar
        self.od = od
        self.combo = combo

    def stringify_pp(self):
        return ""

    def __str__(self):
        message = "[https://osu.ppy.sh/b/%s %s - %s [%s]] " % (self.beatmap_id, self.beatmap["artist"],
                                                               self.beatmap["title"], self.beatmap["version"])

        if self.enabled_mods:
            message += "+%s " % stringify_mods(self.enabled_mods)

        message += self.stringify_pp() + " | "

        if self.combo:
            message += "%dx | " % self.combo

        message += "%s ★ %s ♫ %s AR %s OD %s" % (
            strftime(
                "%M:%S",
                gmtime(
                    time_for_mods(
                        int(self.beatmap["hit_length"]),
                        self.enabled_mods
                    )
                )
            ),
            round(self.stars, 2),
            bpm_for_mods(
                float(self.beatmap["bpm"]), self.enabled_mods
            ),
            round(self.ar, 2),
            round(self.od, 2)
        )
        

        return message
