import logging
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement

from ParserModules.BaseParser import BaseParser
from ParserModules.UserProfileParser import ServiceData


if os.name == 'nt':
    # logging.basicConfig(format=u'[%(levelname)-s] [%(asctime)s] [LINE:%(lineno)d] - %(message)s',
    #                     level=logging.DEBUG)
    # logger = logging.getLogger(__name__)
    pass
else:
    logger = logging.getLogger("debug")


class UserFriendsParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.logins: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type  # todo:

    def run(self) -> list[dict]:
        self.auth_mail_ru()
        result_data = []
        for url in self.logins:

            logger.info(f'opening url -> {url}')
            try:
                self.open_url(url)
            except:
                logger.error(f'Not open url, url -> {url}')
                continue

            if self.is_private(self.driver):
                # logger.info('profile is private')
                continue
            self.switch_to_friends_page(driver=self.driver, url=url)

            friends_data: list[dict] = self.__get_data()
            data = {
                'login': url,
                'data': friends_data
            }
            result_data.append(data)
            print(result_data)
            time.sleep(10000)
        self.driver.close()
        return result_data

    def __get_data(self) -> list[dict]:
        result_data: list[dict] = []
        snipping_double = set()
        counter = 0
        while True:
            friends_tags = self.get_friends_tags(self.driver)
            start_value = len(snipping_double)
            print(f'start_value -> {start_value}')
            for friend_tag in friends_tags:
                link, name = self.get_friend_link(friend_tag)
                if link in snipping_double or link == "None":
                    continue
                else:
                    snipping_double.add(link)
                    result_data.append({
                        "link": link,
                        "name": name
                    })
            self.click_down()
            print(f'counter -> {counter}')
            if start_value < len(snipping_double):
                print('start_value < len(snipping_double)')
                counter = 0
                continue

            if start_value == len(snipping_double):
                print('counter + 1')
                counter += 1

            if counter > 5:
                print('launch break condition')
                return result_data

            else:
                print('not reactable !!!! This is error')
                pass


