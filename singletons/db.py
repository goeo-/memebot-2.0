import asyncio
from collections import defaultdict

from peewee import Model, IntegerField, DoubleField, CharField, TimestampField, DateTimeField
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


class MapData(BaseModel):
    beatmap_id = IntegerField(primary_key=True)
    bpm = DoubleField(index=True)
    max_combo = DoubleField(index=True)
    length = DoubleField(index=True)
    submit_date = DateTimeField(index=True)
    creation_date = DateTimeField(index=True)
    
    cs_nomod = DoubleField(index=True)
    od_nomod = DoubleField(index=True)
    ar_nomod = DoubleField(index=True)
    hp_nomod = DoubleField(index=True)
    star_nomod = DoubleField(index=True)
    
    cs_dt = DoubleField(index=True)
    od_dt = DoubleField(index=True)
    ar_dt = DoubleField(index=True)
    hp_dt = DoubleField(index=True)
    star_dt = DoubleField(index=True)
    
    cs_hrdt = DoubleField(index=True)
    od_hrdt = DoubleField(index=True)
    ar_hrdt = DoubleField(index=True)
    hp_hrdt = DoubleField(index=True)
    star_hrdt = DoubleField(index=True)
    
    cs_ezdt = DoubleField(index=True)
    od_ezdt = DoubleField(index=True)
    ar_ezdt = DoubleField(index=True)
    hp_ezdt = DoubleField(index=True)
    star_ezdt = DoubleField(index=True)
    
    cs_ht = DoubleField(index=True)
    od_ht = DoubleField(index=True)
    ar_ht = DoubleField(index=True)
    hp_ht = DoubleField(index=True)
    star_ht = DoubleField(index=True)
    
    cs_hrht = DoubleField(index=True)
    od_hrht = DoubleField(index=True)
    ar_hrht = DoubleField(index=True)
    hp_hrht = DoubleField(index=True)
    star_hrht = DoubleField(index=True)
    
    cs_ezht = DoubleField(index=True)
    od_ezht = DoubleField(index=True)
    ar_ezht = DoubleField(index=True)
    hp_ezht = DoubleField(index=True)
    star_ezht = DoubleField(index=True)
    
    cs_hr = DoubleField(index=True)
    od_hr = DoubleField(index=True)
    ar_hr = DoubleField(index=True)
    hp_hr = DoubleField(index=True)
    star_hr = DoubleField(index=True)
    
    cs_ez = DoubleField(index=True)
    od_ez = DoubleField(index=True)
    ar_ez = DoubleField(index=True)
    hp_ez = DoubleField(index=True)
    star_ez = DoubleField(index=True)

    class Meta:
        table_name = 'maps_data'
        db_table = 'maps_data'


class Recommended(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=100, index=True)
    beatmap_id = IntegerField(index=True)
    mods = IntegerField(index=True)
    date = TimestampField()
