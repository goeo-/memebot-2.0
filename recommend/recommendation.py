from time import strftime, gmtime

from recommend.maps import find_map, CouldNotFindMapException
from recommend.beatmap import Beatmap, get_beatmap_by_id
from recommend.pp import get_pp_spread
from recommend.target import target, widen_target
from recommend.user import get_user_best
from singletons.config import Config

config = Config()


class Recommendation(Beatmap):
    def __init__(self, beatmap_id, beatmap, enabled_mods, future_you, pp_95, pp_98, pp_99, pp_100, stars, ar, od):
        super().__init__(beatmap_id, beatmap, enabled_mods, stars, ar, od)
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
            widen_target(criteria.targets)
            # if it still can't find a map, the exception will be raised to the recommend handler.
            beatmap_id, enabled_mods, future_you = await find_map(criteria)

        pp_95, pp_98, pp_99, pp_100, stars, ar, od = await get_pp_spread(beatmap_id, enabled_mods)

        beatmap = await get_beatmap_by_id(beatmap_id)
        if not beatmap:
            return await Recommendation.get(criteria)

        return cls(beatmap_id=beatmap_id, beatmap=beatmap, enabled_mods=enabled_mods,
                   future_you=future_you, pp_95=pp_95, pp_98=pp_98, pp_99=pp_99, pp_100=pp_100,
                   stars=stars, ar=ar, od=od)

    def stringify_pp(self):
        return "future you: %s | 95%%: %spp | 98%%: %spp | 99%%: %spp | 100%%: %spp" % (
            round(self.future_you, 2),
            round(self.pp_95, 2),
            round(self.pp_98, 2),
            round(self.pp_99, 2),
            round(self.pp_100, 2)
        )

