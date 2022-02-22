import json
import os
import pickle

from loguru import logger

from setup.config import Config
from src.webdrivermanager import DriverManager


class ParserCookies:
    def __init__(self, config: Config, log: logger, driver: DriverManager):
        self.conf = config
        self.log = log
        self.driver = driver
        self.cookie_data = {}
        self.cookie_data = {}
        self.setup()
        self.load()

    def setup(self) -> None:
        if not os.path.exists(self.conf.parser_cookies_path):
            self.save()

    def load(self) -> None:
        with open(self.conf.parser_cookies_path, 'r') as _cookie:
            self.cookie_data = json.load(_cookie)

    def save(self) -> None:
        with open(self.conf.parser_cookies_path, 'w', encoding='utf-8') as f:
            json.dump(self.cookie_data, f, ensure_ascii=False, indent=4)

    def set(self, key, value) -> None:
        self.cookie_data[key] = value
        self.save()
        self.load()

    def get(self, key) -> bool:
        if key in self.cookie_data:
            return self.cookie_data[key]
        else:
            return False

    def restore(self) -> bool:
        if not os.path.exists(self.conf.cookies_path):
            self.log.warning('Cookies file is empty')
            return False
        self.log.info('Remove default cookies')
        self.driver.delete_all_cookies()
        self.log.info('Start loading cookies from file')
        for cookie in pickle.load(open(self.conf.cookies_path, 'rb')):
            self.driver.add_cookie(cookie)
        return True
