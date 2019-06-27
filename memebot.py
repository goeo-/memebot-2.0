import asyncio
from time import gmtime, strftime, time

import bottom

from handlers import command, action
from singletons.config import Config
from singletons import osu_api


config = Config().config

bot = bottom.Client(host=config['irc']['host'], port=int(config['irc']['port']), ssl=False)
loop = asyncio.get_event_loop()
loop.set_debug(True)  # TODO: remove this?

NICK = config['irc']['nick']
CHANNELS = ["#%s"%x for x in config['irc']['channels'].replace(" ", "").split(",")]

message_send_lock = asyncio.Lock()

bot.last_message = 0


async def keepalive():
    """
    Every five seconds, checks if it's been two minutes since the last time we got a message.
    If it has, the bot will reconnect.

    :return:
    """
    while True:
        await asyncio.sleep(15)
        if time() - bot.last_message >= 120:
            print("got nothing from the irc server in the last two minutes. the connection is probably dead.")
            await reconnect()


async def time_tracker(next_handler, message):
    bot.last_message = time()
    await next_handler(message)

bot.raw_handlers.append(time_tracker)


@bot.on('CLIENT_CONNECT')
async def connect(**kwargs):
    """
    Runs when connected to bancho's IRC.
    Handles logging in and joining channels.

    :param kwargs:
    :return:
    """
    print("connected! sending user data.")

    # Send identifying information.
    bot.send('PASS', password=config['irc']['password'])
    bot.send('NICK', nick=NICK)
    bot.send('USER', user=NICK, realname=NICK)

    # Don't try to join channels until the server has
    # sent the MOTD, or signaled that there's no MOTD.
    done, pending = await asyncio.wait(
        [bot.wait("RPL_ENDOFMOTD"),
         bot.wait("ERR_NOMOTD")],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel whichever waiter's event didn't come in.
    for future in pending:
        future.cancel()

    # Try to join the default channels
    for channel in CHANNELS:
        print("joining %s" % channel)
        bot.send('JOIN', channel=channel)


@bot.on('CLIENT_DISCONNECT')
async def reconnect(**kwargs):
    """
    Runs when our IRC client is disconnected.
    Waits for two seconds and schedules a connection again, and waits for it to happen.

    :param kwargs:
    :return:
    """
    print("reconnecting...")

    await asyncio.sleep(2)

    loop.create_task(bot.connect())

    await bot.wait("CLIENT_CONNECT")


@bot.on('PING')
def ping(message, **kwargs):
    """
    Pongs back pings.

    :param message:
    :param kwargs:
    :return:
    """
    print("got a ping")
    bot.send('PONG', message=message)


@bot.on('PRIVMSG')
def privmsg(**kwargs):
    """
    Handles PRIVMSG's, which can both be messages sent to us directly (pm, /q) or regular channel messages.
    Forwards the two types to their own handlers (DIRECT_MESSAGE and CHANNEL_MESSAGE).

    :param kwargs:
    :return:
    """
    # Don't handle our own messages
    if kwargs["nick"] == NICK:
        return
    # Respond directly to direct messages
    if kwargs["target"] == NICK:
        bot.trigger("DIRECT_MESSAGE", **kwargs)
    # Handle channel messages separately
    else:
        bot.trigger("CHANNEL_MESSAGE",  **kwargs)


async def send_message(target, message):
    print("[%s] <%s=>%s> %s" % (
        strftime("%H:%M:%S", gmtime()),
        NICK,
        target,
        message
    ))

    async with message_send_lock:
        bot.send("PRIVMSG", target=target, message=message)
        await asyncio.sleep(0.5)


@bot.on('DIRECT_MESSAGE')
async def test_message(nick, target, message, **kwargs):
    """
    Runs when a direct message (pm, /q) is received.
    Logs the message to the console, and handles commands.
    :param nick:
    :param target:
    :param message:
    :param kwargs:
    :return:
    """

    # handle ACTIONs (/me, /np in osu)
    if message.startswith("\x01ACTION "):
        print("[%s] <%s=>%s> *%s %s*" % (
            strftime("%H:%M:%S", gmtime()),
            nick,
            target,
            nick,
            message[8:-1]
        ))
        return await send_message(nick, await action.handle(nick, message[8:-1]))

    print("[%s] <%s=>%s> %s" % (
        strftime("%H:%M:%S", gmtime()),
        nick,
        target,
        message
    ))

    # only handle the message if it's a command
    if message.startswith(config["bot"]["prefix"]):
        return await send_message(nick, await command.handle(nick, message[len(config["bot"]["prefix"]):]))

if __name__ == "__main__":
    print("connecting...")
    loop.create_task(bot.connect())
    loop.create_task(keepalive())
    loop.run_forever()
