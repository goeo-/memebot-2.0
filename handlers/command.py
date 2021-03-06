import re

from handlers import recommend, help, reset, np

# Set what handles which regexes
handlers = {
    r'(?i)^r(?:ecommend)?(?: .*)?$': recommend.handler,
    r'(?i)^reset$': reset.handler,
    r'(?i)^h(?:elp)?(?: .*)?$': help.handler,
    r'(?i)^(?:pp|acc(?:uracy)?|with)': np.pp_handler
}

# Compile the regexes so they run faster (we'll be running them for every command!)
for regex in handlers.copy():
    handlers[re.compile(regex)] = handlers.pop(regex)


async def handle(user, message):
    """
    Chooses what handler to forward the command to by going through regexes defined in `handlers`
    If it can't find any regexes that match the command, it will send a default response.

    :param user:
    :param message:
    :return:
    """
    for regex_, handler in handlers.items():
        if regex_.match(message):
            return await handler(user, message)
    return "No such command. Use the !help command for more information."
