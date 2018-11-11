from singletons.singleton import singleton
from singletons.config import Config
import aiohttp


@singleton
class OsuAPI:
    def __init__(self, session):
        self.session = session

    async def call(self, endpoint, params):
        params["k"] = Config().config["osu"]["api_key"]
        async with self.session.get("%s%s" % (Config().config["osu"]["api_url"], endpoint), params=params) as resp:
            return await resp.json()


async def init():
    return OsuAPI(aiohttp.ClientSession())