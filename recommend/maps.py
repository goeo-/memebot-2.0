from singletons.db import *
from peewee import JOIN
from recommend.future_you import future_you
from recommend.user import get_user_best
from functools import reduce
import operator
from datetime import datetime, timedelta


async def find_map(criteria):
    # queue the db based on criteria, return the most farmy map not already recommended
    clauses = [
        (Recommended.id.is_null()),
        (Map.acc_pp <= criteria.targets.target_acc_pp),
        (Map.aim_pp <= criteria.targets.target_aim_pp),
        (Map.speed_pp <= criteria.targets.target_speed_pp),
        (Map.total_pp.between(criteria.targets.target_total_pp, criteria.targets.target_total_pp_max))
    ]

    if criteria.mods:
        if criteria.mods == -1:
            clauses.append((Map.enabled_mods == 0))
        else:
            clauses.append((Map.enabled_mods.bin_and(criteria.mods)))

    query = Map.select()\
               .join(Recommended, JOIN.LEFT_OUTER, on=((Recommended.beatmap_id == Map.beatmap_id) &
                                                       (Recommended.mods.bin_and(Map.enabled_mods)) &
                                                       (Recommended.username == criteria.user) &
                                                       (Recommended.date < datetime.now() - timedelta(days=30))))\
               .where(reduce(operator.and_, clauses))

    async with Database().user_locks[criteria.user]:
        try:
            results = await Database().objects.execute(query)
        except Map.DoesNotExist:
            raise CouldNotFindMapException

    user_best = await get_user_best(criteria.user)

    for result in results:
        # check if in top plays of user
        # if so, add to recommended, continue
        async with Database().user_locks[criteria.user]:
            await Database().objects.create(Recommended, beatmap_id=result.beatmap_id, mods=result.enabled_mods,
                                            username=criteria.user)
        for play in user_best:
            if play['beatmap_id'] == result.beatmap_id and play['enabled_mods'] & result.enabled_mods:
                continue
        return result.beatmap_id, result.enabled_mods, await future_you(criteria.user, result.beatmap_id, result.enabled_mods)


class CouldNotFindMapException(Exception):
    pass


'''
    if criteria.max_creation_date:
        clauses.append(())
    if criteria.max_length:
        clauses.append(())
    if criteria.max_combo:
        clauses.append(())
    if criteria.max_ar:
        clauses.append(())
    if criteria.max_od:
        clauses.append(())
    if criteria.max_cs:
        clauses.append(())
    if criteria.max_bpm:
        clauses.append(())
    if criteria.min_creation_date:
        clauses.append(())
    if criteria.min_length:
        clauses.append(())
    if criteria.min_combo:
        clauses.append(())
    if criteria.min_ar:
        clauses.append(())
    if criteria.min_od:
        clauses.append(())
    if criteria.min_cs:
        clauses.append(())
    if criteria.min_bpm:
        clauses.append(())
'''