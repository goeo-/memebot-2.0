from singletons.singleton import singleton
import configparser


@singleton
class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")