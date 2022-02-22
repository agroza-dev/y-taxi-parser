import math
import re
import time
from string import Template

import notifiers
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from setup.config import Config, AddressItem
from src.auth import Auth
from src.cookies import ParserCookies
from src.webdrivermanager import DriverManager


class Parser:
    def __init__(self, driver: DriverManager,  config: Config, log: logger, cookies: ParserCookies):
        self.driver = driver
        self.conf = config
        self.log = log
        self.cookies = cookies
        self.telegram = notifiers.get_notifier('telegram')

    def run(self):
        try:
            auth = Auth(self.driver, self.conf, self.cookies, self.log)
            if not (auth.restore_from_cookies()):
                self.log.info('Auth by cookies failed')
                self.log.info('Try to auth by login & password')
                if not (auth.login()):
                    raise Exception('Auth by login & password - failed!')

            self.log.info('Start parsing')

            errors_on_receiving_prices = 0
            prices_sum = 0
            for address in self.conf.Parser.addresses:
                self.fill_address_a(address, self.conf)
                time.sleep(2)
                self.fill_address_b(address, self.conf)

                time.sleep(5)
                self.log.info(f'Starting parse first tariff block')
                raw_price = None
                for key, path in enumerate(self.conf.Navigate.first_tariff_price_paths):
                    self.log.info(f'Try to parse {key} path {path}')
                    raw_price = self.driver.get_element_text(path)
                    self.log.info(f'Received value: {raw_price}')
                    if raw_price:
                        break

                if not raw_price:
                    self.log.warning('Bad price. This step wil be skipped')
                    errors_on_receiving_prices += 1
                    continue
                formatted_price = self.get_numbers_from_string(raw_price)
                if not formatted_price:
                    self.log.warning('Bad price after formatting. This step wil be skipped')
                    errors_on_receiving_prices += 1
                    continue
                prices_sum += formatted_price

            addresses = self.conf.Parser.addresses
            if errors_on_receiving_prices > 0:
                self.notify(Template(self.conf.Parser.msg['error']).substitute(
                    count_errors=errors_on_receiving_prices, total_addresses_count=len(addresses)
                ))
                raise Exception(
                    f'Not all prices was received. Cant get average prices value. Exit without calculations')

            self.log.info('All prices received successful. Start calculations.')
            average_price = math.ceil(prices_sum / len(addresses))
            self.log.info(f'Average_value = {average_price} | Max_threshold = {self.conf.Parser.max_threshold}')
            if average_price > self.conf.Parser.max_threshold:
                self.notify(Template(self.conf.Parser.msg['start_high_demand']).substitute(price=average_price))
                self.log.info(f'High demand started. Notify sent.')
                self.cookies.set('is_notify_sent', True)
            else:
                if self.cookies.get('is_notify_sent'):
                    self.notify(Template(self.conf.Parser.msg['end_high_demand']).substitute(price=average_price))
                    self.log.info(f'High demand ended. Notify sent.')
                self.cookies.set('is_notify_sent', False)
        except Exception as e:
            if self.log:
                self.log.critical(str(e))
        finally:
            time.sleep(3)
            if self.driver:
                self.driver.destroy()

    def fill_address_a(self, address: AddressItem, conf: Config):
        self.log.info(f'Start sending keys for address: "a" ({address.a})')
        self.fill_address(address.a, conf.Navigate.a_input)

    def fill_address_b(self, address: AddressItem, conf: Config):
        self.log.info(f'Start sending keys for address: "b" ({address.b})')
        self.fill_address(address.b, conf.Navigate.b_input)

    def fill_address(self, address: str, path_to_element: str):
        _input = self.driver.send_keys(path_to_element, address, By.XPATH, True)
        if not _input:
            self.driver.make_screenshot(f'input_address_error')
            raise Exception(f'Can`t fill address.')
        self.log.info(f'Address filled')
        time.sleep(3)
        self.log.info('Waiting before click PAGE_DOWN key')
        self.driver.send_keys(path_to_element, Keys.ARROW_DOWN, By.XPATH, False)
        self.log.info('PAGE_DOWN clicked')
        self.log.info('Waiting before click ENTER key')
        time.sleep(1)
        self.driver.send_keys(path_to_element, Keys.ENTER, By.XPATH, False)
        self.log.info('ENTER clicked')
        time.sleep(3)

    def get_numbers_from_string(self, raw_string: str) -> int:
        result = False
        try:
            found_matches = re.search(r'([0-9]{1,6})', raw_string)
            self.log.debug(f'Price matches: {found_matches}')
            if found_matches.group(0):
                result = int(found_matches.group(0))
        except Exception as e:
            self.log.error(f'{str(e)} when try to get numbers from string: {raw_string}')
        finally:
            return result

    def notify(self, text: str):
        for chat_id in self.conf.Tg.recipient_ids:
            self.telegram.notify(message=text, token=self.conf.Tg.bot_token, chat_id=chat_id)
