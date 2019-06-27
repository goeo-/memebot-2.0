from oppai import *
from singletons.config import Config
import aiohttp
import aiofiles
import aiofiles.os


async def download_map(beatmap_id):
    path = '%s/%s.osu' % (Config().config['oppai']['map_dir'], beatmap_id)

    async with aiohttp.ClientSession() as session:
        async with session.get('https://osu.ppy.sh/osu/%s' % beatmap_id) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()


async def ensure_map_exists(beatmap_id):
    path = '%s/%s.osu' % (Config().config['oppai']['map_dir'], beatmap_id)

    try:
        stat = await aiofiles.os.stat(path)
    except FileNotFoundError:
        return await download_map(beatmap_id)
    if stat.st_size == 0:
        return await download_map(beatmap_id)


async def get_pp_spread(beatmap_id, enabled_mods):
    # get spread (95, 98, 99, 100 acc pps)
    await ensure_map_exists(beatmap_id)
    ez = ezpp_new()
    ezpp_set_autocalc(ez, 1)
    ezpp_dup(ez, '%s/%s.osu' % (Config().config['oppai']['map_dir'], beatmap_id))
    ezpp_set_mods(ez, enabled_mods)
    ezpp_set_accuracy_percent(ez, 95)
    pp95 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 98)
    pp98 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 99)
    pp99 = ezpp_pp(ez)
    ezpp_set_accuracy_percent(ez, 100)
    pp100 = ezpp_pp(ez)
    ezpp_free(ez)
    return pp95, pp98, pp99, pp100


async def get_pps(beatmap_id, enabled_mods, maxcombo, countmiss, count50, count100):
    # returns total_pp, aim_pp, speed_pp, acc_pp
    await ensure_map_exists(beatmap_id)
    ez = ezpp_new()
    ezpp_set_mods(ez, enabled_mods)

    if maxcombo:
        ezpp_set_combo(ez, maxcombo)
    if countmiss:
        ezpp_set_nmiss(ez, countmiss)
    if count100 and count50:
        ezpp_set_accuracy(ez, count100, count50)

    ezpp(ez, '%s/%s.osu' % (Config().config['oppai']['map_dir'], beatmap_id))
    ret = (ezpp_pp(ez), ezpp_aim_pp(ez), ezpp_speed_pp(ez), ezpp_acc_pp(ez))
    ezpp_free(ez)
    return ret
