from recommend.pp import get_pps


class Target:
    __slots__ = ['target_acc_pp', 'target_aim_pp', 'target_speed_pp', 'target_total_pp', 'target_total_pp_max']

    def __init__(self, acc, aim, speed, total, total_max):
        self.target_acc_pp = acc
        self.target_aim_pp = aim
        self.target_speed_pp = speed
        self.target_total_pp = total
        self.target_total_pp_max = total_max


class NoPlaysException(Exception):
    pass


async def target(user_best):
    # set target aim, acc, speed, total, total_max pp for user.
    # make the target wider as the user gets better
    top_plays_amount = 0
    total_pp = 0
    aim_pp = 0
    speed_pp = 0
    acc_pp = 0
    for score in user_best[2:]:
        if top_plays_amount == 20:
            break

        total_pp_t, aim_pp_t, speed_pp_t, acc_pp_t = await get_pps(score["beatmap_id"],    int(score["enabled_mods"]),
                                                                   int(score["maxcombo"]), int(score["countmiss"]),
                                                                   int(score["count50"]),  int(score["count100"]))
        top_plays_amount += 1
        total_pp += total_pp_t
        aim_pp += aim_pp_t
        speed_pp += speed_pp_t
        acc_pp += acc_pp_t

    if top_plays_amount == 0:
        raise NoPlaysException

    total_pp = total_pp / top_plays_amount
    aim_pp = aim_pp / top_plays_amount
    speed_pp = speed_pp / top_plays_amount
    acc_pp = acc_pp / top_plays_amount

    return Target(acc_pp+60, aim_pp+60, speed_pp+60, total_pp+40, total_pp+200)


def widen_target(target):
    # raise the target by an amount that depends on how big the target was
    target.target_acc_pp += 20
    target.target_aim_pp += 20
    target.target_speed_pp += 20
    target.target_total_pp -= 20
    target.target_total_pp_max += 80
