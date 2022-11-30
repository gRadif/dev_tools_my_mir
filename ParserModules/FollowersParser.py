import logging
import time
from pprint import pprint

from ParserModules.BaseParser import BaseParser
from ParserModules.UserProfileParser import ServiceData

logger = logging.getLogger("debug")


class FollowersParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.logins: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type

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
                logger.info('profile is private')
                continue

            followers_data: list[dict] = self.__get_data(url)
            data = {'login': url,
                    'data': followers_data}
            result_data.append(data)
        logger.info(f'FollowerParser finish the job')
        pprint(result_data)
        time.sleep(10000)
        return result_data

    def __get_data(self, url) -> list[dict]:
        result_data: list[dict] = []
        friends_url = self.__prepare_url(url)
        for page in range(1, 26):
            if page == 1:
                self.open_url(friends_url)
                result_data.extend(self.get_channel_followers(self.driver))
            else:
                self.open_url(friends_url + '?page=' + f"{page}")
                result_data.extend(self.get_channel_followers(self.driver))
                logger.info(f'from page -> {page} data collected')
        return result_data

    def __prepare_url(self, url) -> str:
        url = url.replace('?ref=srch', '')
        if url[-1] == "/":
            friends_url = url + 'friends'
        else:
            friends_url = url + '/friends'
        return friends_url
