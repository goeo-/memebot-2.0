from time import time
from singletons.osu_api import OsuAPI


user_top_plays = {
    # "username": (cache time, [top plays])
}


async def get_user_best(username):
    if username in user_top_plays:
        if time() <= user_top_plays[username][0] + 600:
            return user_top_plays[username][1]

    best = await OsuAPI().call("get_user_best", {"type": "string", "limit": 100, "u": username})
    user_top_plays[username] = (time(), best)
    return user_top_plays[username][1]