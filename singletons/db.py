import asyncio
from collections import defaultdict

from peewee import Model, IntegerField, DoubleField, CharField, TimestampField
from peewee_async import Manager, PooledMySQLDatabase

from singletons.config import Config
from singletons.singleton import singleton


@singleton
class Database:
    def __init__(self):
        self.database = PooledMySQLDatabase(Config()['sql']['db'], user=Config()['sql']['user'],
                                            password=Config()['sql']['password'],
                                            host=Config()['sql']['host'],
                                            port=int(Config()['sql']['port']), max_connections=10)

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
    date = TimestampField()
