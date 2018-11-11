from parsers.recommendation_criteria import parse_criteria

user_top_plays = {
    # "username": (cache time, [top plays])
}

async def handler(user, message):
    criteria = parse_criteria(user, message)
    recommendation = recommend(criteria)
    return form_message(recommendation)


class CouldNotDownloadBeatmapException(Exception):
    pass


'''
Map
.select()
.join(Recommended, JOIN.LEFT_OUTER, on=(Recommended.beatmap_id == Map.beatmap_id &
                                        Recommended.mods.bin_and(Map.enabled_mods) &
                                        Recommended.username == user &
                                        Recommended.date + 2592000 < time.time()))
.where(Recommended.id.is_null() &
       Map.acc_pp <= target_acc_pp &
       Map.aim_pp <= target_aim_pp &
       Map.speed_pp <= target_speed_pp &
       Map.total_pp.between(target_total_pp, target_total_pp_max))
'''