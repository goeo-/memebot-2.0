from recommend.pp import get_pps
from recommend.target import NoPlaysException
from recommend.user import get_user_best


async def future_you(user, beatmap_id, enabled_mods):
    user_best = await get_user_best(user)
    top_plays_amount = 0
    aim_pp = 0
    speed_pp = 0
    acc_pp = 0
    for score in user_best[5:25]:
        _, aim_pp_t, speed_pp_t, acc_pp_t = await get_pps(score["beatmap_id"], int(score["enabled_mods"]),
                                                          int(score["maxcombo"]), int(score["countmiss"]),
                                                          int(score["count50"]), int(score["count100"]))
        top_plays_amount += 1
        aim_pp += aim_pp_t
        speed_pp += speed_pp_t
        acc_pp += acc_pp_t

    if top_plays_amount == 0:
        raise NoPlaysException

    aim_pp = aim_pp / top_plays_amount
    speed_pp = speed_pp / top_plays_amount
    acc_pp = acc_pp / top_plays_amount

    _, aim_pp_t, speed_pp_t, acc_pp_t = await get_pps(beatmap_id, enabled_mods,
                                                      None, None, None, None)

    return min(aim_pp, aim_pp_t) + min(speed_pp, speed_pp_t) + min(acc_pp, acc_pp_t)
