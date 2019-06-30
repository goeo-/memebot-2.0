from singletons.db import Database, Recommended


async def handler(user, message):
    query = Recommended.delete().where(Recommended.username == user)
    async with Database().user_locks[user]:
        result = await Database().objects.execute(query)
    return 'Successfully reset recommendation status of %s maps.' % result
