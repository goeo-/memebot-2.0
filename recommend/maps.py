import operator
from datetime import datetime, timedelta
from functools import reduce

from peewee import JOIN

from recommend.future_you import future_you
from recommend.user import get_user_best
from recommend.mods import ModFlag, has_mod, stringify_mods
from singletons.db import *

modded_filters = ["star", "cs", "od", "ar", "hp"]


def get_modstring(base, filter_mods):
    return base + "_" + ("nomod" if filter_mods == 0 else stringify_mods(filter_mods).lower())


def scale_time(time, actual_mods):
    if has_mod(actual_mods, ModFlag.DoubleTime):
        time *= 1.5
    if has_mod(actual_mods, ModFlag.HalfTime):
        time /= 1.5
    return time


async def find_map(criteria):
    # queue the db based on criteria, return the most farmy map not already recommended
    clauses = [
        (Recommended.id.is_null()),
        (Map.acc_pp <= criteria.targets.target_acc_pp),
        (Map.aim_pp <= criteria.targets.target_aim_pp),
        (Map.speed_pp <= criteria.targets.target_speed_pp),
        (Map.total_pp.between(criteria.targets.target_total_pp, criteria.targets.target_total_pp_max))
    ]

    # only care about EZ, HD, HR, DT, HT, FL, TD
    actual_mods = criteria.mods & 1374
    filter_mods = criteria.mods & (ModFlag.DoubleTime + ModFlag.HalfTime + ModFlag.HardRock + ModFlag.Easy)

    if criteria.mods:
        if criteria.mods == -1: # NOMOD criteria
            actual_mods = 0
            filter_mods = 0
            clauses.append((Map.enabled_mods == 0))
        else:
            clauses.append((Map.enabled_mods.bin_and(actual_mods) == actual_mods))
        
        # don't recommend touchscreen plays unless explicitly asked for
        if not has_mod(criteria.mods, ModFlag.TouchDevice):
            clauses.append((Map.enabled_mods.bin_and(ModFlag.TouchDevice) == 0))

    if criteria.notmods:
        clauses.append((Map.enabled_mods.bin_and(criteria.notmods) == 0))

    if criteria.max_length:
        clauses.append((MapData.length <= scale_time(criteria.max_length, actual_mods)))
    if criteria.max_bpm:
        clauses.append((MapData.bpm <= scale_time(criteria.max_bpm, actual_mods)))
    if criteria.max_combo:
        clauses.append((MapData.max_combo <= criteria.max_combo))
    if criteria.max_creation_date:
        clauses.append((MapData.creation_date <= criteria.max_creation_date))

    if criteria.min_length:
        clauses.append((MapData.length >= scale_time(criteria.min_length, actual_mods)))
    if criteria.min_bpm:
        clauses.append((MapData.bpm >= scale_time(criteria.min_bpm, actual_mods)))
    if criteria.min_combo:
        clauses.append((MapData.min_combo >= criteria.min_combo))
    if criteria.min_creation_date:
        clauses.append((MapData.creation_date >= criteria.min_creation_date))

    # handle stars, cs, od, ar, hp
    for filter in modded_filters:
        modstring = get_modstring(filter, filter_mods)

        if getattr(criteria, "max_" + filter):
            clauses.append((getattr(MapData, modstring) <= getattr(criteria, "max_" + filter)))
        if getattr(criteria, "min_" + filter):
            clauses.append((getattr(MapData, modstring) >= getattr(criteria, "min_" + filter)))

    query = Map.select() \
        .join(Recommended, JOIN.LEFT_OUTER, on=(
            (Recommended.beatmap_id == Map.beatmap_id) &
            (Recommended.mods.bin_and(Map.enabled_mods) == Recommended.mods) &
            (Recommended.username == criteria.user) &
            (Recommended.date > datetime.now() - timedelta(days=30))
         )) \
        .switch(Map) \
        .join(MapData, JOIN.LEFT_OUTER, on=(MapData.beatmap_id == Map.beatmap_id)) \
        .where(reduce(operator.and_, clauses)) \
        .order_by(Map.farminess.desc()) \
        .limit(1)

    user_best = await get_user_best(criteria.user)

    while True:
        async with Database().user_locks[criteria.user]:
            try:
                result = await Database().objects.get(query)
            except Map.DoesNotExist:
                raise CouldNotFindMapException()
            await Database().objects.create(Recommended, beatmap_id=result.beatmap_id, mods=result.enabled_mods,
                                            username=criteria.user, date=datetime.now())
        # check if in top plays of user, if in there continue

        for play in user_best:
            if play['beatmap_id'] == result.beatmap_id and \
               play['enabled_mods'] & result.enabled_mods == play['enabled_mods']:
                continue
        return result.beatmap_id, result.enabled_mods, await future_you(criteria.user,
                                                                        result.beatmap_id,
                                                                        result.enabled_mods)


class CouldNotFindMapException(Exception):
    pass
class InvalidDateException(Exception):
    pass
