import asyncio
from peewee_async import Manager, PooledMySQLDatabase
from singletons.singleton import singleton
from singletons.config import Config
from collections import defaultdict
from peewee import Model, IntegerField, DoubleField, CharField, TimestampField


@singleton
class Database:
    def __init__(self):
        self.database = PooledMySQLDatabase(Config().config['sql']['db'], user=Config().config['sql']['user'],
                                            password=Config().config['sql']['password'],
                                            host=Config().config['sql']['host'],
                                            port=int(Config().config['sql']['port']), max_connections=10)

        self.objects = Manager(self.database, loop=asyncio.get_event_loop())
        self.objects.database.allow_sync = False

        self.user_locks = defaultdict(asyncio.Lock)


class BaseModel(Model):
    class Meta:
        database = Database().database


class Map(BaseModel):
    id = IntegerField(primary_key=True)
    beatmap_id = IntegerField()
    enabled_mods = IntegerField()
    aim_pp = DoubleField(index=True)
    speed_pp = DoubleField(index=True)
    acc_pp = DoubleField(index=True)
    total_pp = DoubleField(index=True)
    farminess = IntegerField(index=True)

    class Meta:
        table_name = 'maps'
        db_table = 'maps'


class Recommended(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=100, index=True)
    beatmap_id = IntegerField(index=True)
    mods = IntegerField(index=True)
    date = IntegerField()
