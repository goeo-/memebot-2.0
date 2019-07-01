import aiohttp

from singletons.config import Config
from singletons.singleton import singleton


@singleton
class OsuAPI:
    def __init__(self):
        self.session = None

    async def call(self, endpoint, params):
        if not self.session:
            self.session = aiohttp.ClientSession()
        params["k"] = Config().config["osu"]["api_key"]
        async with self.session.get("%s%s" % (Config().config["osu"]["api_url"], endpoint), params=params) as resp:
            return await resp.json()
