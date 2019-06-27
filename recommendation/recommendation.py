from singletons.config import Config
from singletons.osu_api import OsuAPI
from parsers.recommendation_criteria import stringify_mods
from time import strftime, gmtime, time
from recommendation.target import target, widen_target
from recommendation.maps import find_map, CouldNotFindMapException
from recommendation.pp import get_pp_spread


user_top_plays = {
    # "username": (cache time, [top plays])
}

config = Config().config


def time_for_mods(time, mods_enabled):
    if mods_enabled & 64 == 64:
        return int(time * 0.75)
    return time


def bpm_for_mods(bpm, mods_enabled):
    if mods_enabled & 64 == 64:
        return int(bpm * 1.5)
    else:
        return int(bpm)


async def get_user_best(username):
    if username in user_top_plays:
        if time() <= user_top_plays[username][0] + 600:
            return user_top_plays[username][1]

    best = await OsuAPI().call("get_user_best", {"type": "string", "limit": 100, "u": username})
    user_top_plays[username] = (time(), best)
    return user_top_plays[username][1]


class Recommendation:
    def __init__(self, beatmap_id, beatmap, enabled_mods, future_you, pp_95, pp_98, pp_99, pp_100):
        self.beatmap_id = beatmap_id
        self.beatmap = beatmap
        self.enabled_mods = enabled_mods
        self.future_you = future_you
        self.pp_95 = pp_95
        self.pp_98 = pp_98
        self.pp_99 = pp_99
        self.pp_100 = pp_100

    @classmethod
    async def get(cls, criteria):
        user_best = await get_user_best(criteria.user)
        criteria.targets = await target(user_best)

        try:
            beatmap_id, enabled_mods, future_you = await find_map(criteria)
        except CouldNotFindMapException:
            criteria.targets = widen_target(criteria.targets)
            # if it still can't find a map, the exception will be raised to the recommendation handler.
            beatmap_id, enabled_mods, future_you = await find_map(criteria)

        pp_95, pp_98, pp_99, pp_100 = await get_pp_spread(beatmap_id, enabled_mods)

        beatmap = await OsuAPI().call("get_beatmaps", {"b": beatmap_id, "m": 0})
        return cls(beatmap_id=beatmap_id, beatmap=beatmap, enabled_mods=enabled_mods,
                   future_you=future_you, pp_95=pp_95, pp_98=pp_98, pp_99=pp_99, pp_100=pp_100)

    def __str__(self):
        message = "[%s%s %s - %s [%s]] " % (config["osu"]["beatmap_url"], self.beatmap_id, self.beatmap["artist"],
                                            self.beatmap["title"], self.beatmap["version"])

        if self.enabled_mods:
            message += "+%s " % stringify_mods(self.enabled_mods)

        message += "future you: %s | 95%%: %spp | 98%%: %spp  | 99%%: %spp | 100%%: %spp | " % (
            round(self.future_you, 2),
            round(self.pp_95, 2),
            round(self.pp_98, 2),
            round(self.pp_99, 2),
            round(self.pp_100, 2)
        )

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