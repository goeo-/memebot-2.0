import re

from recommend.beatmap import Beatmap, get_beatmap_by_id
from recommend.mods import ModFlag, stringify_mods, modsify_string, mods_regex
from recommend.pp import get_pp_spread, get_pp
from singletons.osu_api import OsuAPI

# Used to remember the map for the !pp command
user_np_cache = {}
acc_regex = re.compile(r'\d+(?:\.\d+)?%?')
  

async def np_handler(user, message, match):
    parts = match.groupdict()

    # Parse the mods from the np string
    enabled_mods = 0
    if parts['mods']:
        try:
            raw_mods = parts['mods'].strip().split(' ')
            enabled_mods = sum([ModFlag[name.strip('-+~|')].value for name in raw_mods])
        except KeyError:
            return 'Invalid mod list. Please use /np.'

    beatmap_id = int(parts['id'])
    user_np_cache[user] = beatmap_id

    return await calculate_np(beatmap_id, enabled_mods)


async def calculate_np(beatmap_id, enabled_mods):
    pp_95, pp_98, pp_99, pp_100, stars, ar, od = await get_pp_spread(beatmap_id, enabled_mods)

    beatmap = await get_beatmap_by_id(beatmap_id)
    if not beatmap:
        return 'Error getting beatmap information.'

    np_map = NPMap(beatmap_id, beatmap, enabled_mods, None, None, pp_95, pp_98, pp_99, pp_100, stars, ar, od)
    return np_map


async def pp_handler(user, message):
    try:
        beatmap_id = user_np_cache[user]
    except KeyError:
        return 'Run /np first! Use the !help command for more information.'
    
    objects = message.split(" ")
    if len(objects) < 2:
        return 'Please specify the accuracy or mods. Use the !help command for more information.'

    enabled_mods = 0
    accuracy = None

    for obj in objects[1:]:
        if mods_regex.match(obj):
            enabled_mods = modsify_string(obj)
        elif acc_regex.match(obj):
            accuracy = max(min(float(obj.rstrip("%")), 100), 0)

    if accuracy:
        return await calculate_pp(beatmap_id, enabled_mods, accuracy)
    else:
        return await calculate_np(beatmap_id, enabled_mods)


async def calculate_pp(beatmap_id, enabled_mods, accuracy):
    pp, stars, ar, od = await get_pp(beatmap_id, enabled_mods, accuracy)

    beatmap = await get_beatmap_by_id(beatmap_id)
    if not beatmap:
        return 'Error getting beatmap information.'

    pp_map = NPMap(beatmap_id, beatmap, enabled_mods, accuracy, pp, None, None, None, None, stars, ar, od)
    return pp_map


class NPMap(Beatmap):
    def __init__(self, beatmap_id, beatmap, enabled_mods, accuracy, pp, pp_95, pp_98, pp_99, pp_100, stars, ar, od):
        super().__init__(beatmap_id, beatmap, enabled_mods, stars, ar, od)
        self.accuracy = accuracy
        self.pp = pp
        self.pp_95 = pp_95
        self.pp_98 = pp_98
        self.pp_99 = pp_99
        self.pp_100 = pp_100

    def stringify_pp(self):
        if self.accuracy:
            return '%s%%: %spp' % (
                round(self.accuracy, 2),
                round(self.pp, 2)
            )
        else:
            return '95%%: %spp | 98%%: %spp | 99%%: %spp | 100%%: %spp' % (
                round(self.pp_95, 2),
                round(self.pp_98, 2),
                round(self.pp_99, 2),
                round(self.pp_100, 2)
            )
