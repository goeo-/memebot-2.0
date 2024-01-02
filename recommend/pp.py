import aiofiles
import aiofiles.os
import aiohttp
from rosu_pp_py import Beatmap, Calculator

from singletons.config import Config


async def download_map(beatmap_id):
    path = '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id)

    async with aiohttp.ClientSession() as session:
        async with session.get('https://osu.ppy.sh/osu/%s' % beatmap_id) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()


async def ensure_map_exists(beatmap_id):
    path = '%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id)

    try:
        stat = await aiofiles.os.stat(path)
    except FileNotFoundError:
        return await download_map(beatmap_id)
    if stat.st_size == 0:
        return await download_map(beatmap_id)


async def get_pp_spread(beatmap_id, enabled_mods, combo=None):
    # get spread (95, 98, 99, 100 acc pps)
    await ensure_map_exists(beatmap_id)
    map = Beatmap(path='%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))
    calc = Calculator()

    if enabled_mods & 4:
        calc.set_mods(enabled_mods ^ 64)

    calc.set_mods(enabled_mods)

    if combo:
        calc.set_combo(combo)

    calc.set_acc(95)
    pp95 = calc.performance(map).pp
    calc.set_acc(98)
    pp98 = calc.performance(map).pp
    calc.set_acc(99)
    pp99 = calc.performance(map).pp
    calc.set_acc(100)
    pp100 = calc.performance(map).pp
    diff = calc.difficulty(map)
    stars = diff.stars
    ar = diff.ar
    od = diff.od

    return pp95, pp98, pp99, pp100, stars, ar, od


async def get_pp(beatmap_id, enabled_mods, accuracy, combo=None):
    # returns total_pp for a specific accuracy
    await ensure_map_exists(beatmap_id)
    map = Beatmap(path='%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))
    calc = Calculator()

    if enabled_mods & 4:
        calc.set_mods(enabled_mods ^ 64)

    calc.set_mods(enabled_mods)

    if combo:
        calc.set_combo(combo)

    calc.set_acc(accuracy)
    pp = calc.performance(map).pp
    diff = calc.difficulty(map)
    stars = diff.stars
    ar = diff.ar
    od = diff.od
    return pp, stars, ar, od


async def get_pps(beatmap_id, enabled_mods, maxcombo, countmiss, count50, count100):
    # returns total_pp, aim_pp, speed_pp, acc_pp
    await ensure_map_exists(beatmap_id)
    map = Beatmap(path='%s/%s.osu' % (Config()['oppai']['map_dir'], beatmap_id))
    calc = Calculator()

    if enabled_mods & 4:
        calc.set_mods(enabled_mods ^ 64)

    calc.set_mods(enabled_mods)

    if maxcombo:
        calc.set_combo(maxcombo)
    if countmiss:
        calc.set_n_misses(countmiss)
    if count100 and count50:
        calc.set_n100(count100)
        calc.set_n50(count50)

    perf = calc.performance(map)
    ret = (perf.pp, perf.pp_aim, perf.pp_speed, perf.pp_acc)
    return ret
