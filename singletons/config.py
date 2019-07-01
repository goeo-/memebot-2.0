import configparser

from singletons.singleton import singleton


@singleton
class Config:
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read("config.ini")

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, key, value):
        self._config[key] = value
