from loguru import logger
from notifiers.logging import NotificationHandler

from setup.config import Config


class Logger:
    def __init__(self, conf: Config):
        self.log = logger
        self.conf = conf
        telegram_handler = NotificationHandler("telegram", defaults={
            "chat_id": self.conf.Tg.alarm_chat_id,
            "token": self.conf.Tg.bot_token,
        })
        self.log.add(
            sink=self.conf.Log.path,
            level=self.conf.Log.level,
            format=self.conf.Log.format,
            retention=self.conf.Log.retention,
            encoding=self.conf.Log.encoding
        )
        self.log.add(telegram_handler, level="ERROR", format=self.conf.Log.tg_format)

    def get_instance(self) -> logger:
        return self.log
