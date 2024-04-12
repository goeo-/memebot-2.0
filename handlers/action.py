import re

from handlers import np

# Set what handles which regexes
handlers = {
    r'^(?:is listening to|is playing|is watching|is editing) \[https?:\/\/osu\.ppy\.sh\/b(?:eatmapsets\/.*?#.*?)?\/(?P<id>\d+).*\](?: <osu!.*?>)?(?P<mods>(?: (?:[-+~|]\w+[~|]?))*)$': np.np_handler
}

# Compile the regexes so they run faster (we'll be running them for every command!)
for regex in handlers.copy():
    handlers[re.compile(regex)] = handlers.pop(regex)


# noinspection PyUnusedLocal
async def handle(user, message):
    """
    Chooses what handler to forward the command to by going through regexes defined in `handlers`
    If it can't find any regexes that match the command, it will send a default response.
    """
    for regex_, handler in handlers.items():
        match = regex_.match(message)
        if match:
            return await handler(user, message, match)
    return "No such command. Use the !help command for more information."
