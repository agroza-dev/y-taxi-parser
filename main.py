import time

import schedule

from setup.config import Config
from src.app import Parser
from src.cookies import ParserCookies
from src.logger import Logger
from src.webdrivermanager import DriverManager


def run(parser, driver):
    driver.init()
    parser.run()


def main():
    conf = Config()
    logger = Logger(conf).get_instance()
    driver = DriverManager(conf, logger)
    cookies = ParserCookies(conf, logger, driver)
    parser = Parser(driver, conf, logger, cookies)

    schedule.every(conf.running_schedule_in_minutes).minutes.at(':00').do(run, parser=parser, driver=driver)

    while True:
        schedule.run_pending()
        time.sleep(conf.Wait.s_1)


if __name__ == '__main__':
    main()
