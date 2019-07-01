import configparser

from singletons.singleton import singleton


@singleton
class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
