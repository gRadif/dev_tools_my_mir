import logging
import time
from pprint import pprint

from selenium.webdriver.common.by import By

from ParserModules.BaseParser import BaseParser, PageNotFoundError, ProfileIsPrivateError
from ParserModules.UserProfileParser import ServiceData

class MainError(BaseException):
    pass


logger = logging.getLogger(__name__)


class PostCommentsAndLikesParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.logins: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type
        self.BASE_URL = 'https://my.mail.ru'
        self.result_data = []
        self.channels_failed = []

    def launch(self) -> list[dict]:
        logger.debug(f'input urls -> {self.logins}')
        print(f'input urls -> {self.logins}')
        self.auth_mail_ru()
        for url in self.logins:


            logger.info(f'opening url -> {url}')
            print(f'opening url -> {url}')
            try:
                self.open_url(url)
                # self.checking_page_not_found()
                # self.checking_private_page()
                data: dict = self.__collect_data(url)
                if len(data['comments_data']) == 0 or len(data['likers_data']) == 0:
                    logger.critical('errrorrrrrr')
                    # TaskStatus_(task_id=self.task_id,
                    #             task_type=self.task_type,
                    #             login=url).warning(change_asup=True, change_local=False)
                self.result_data.append(data)

            except PageNotFoundError as desc:
                stacktrace = f'{desc}'
                self._error_handler(url, stacktrace)
                continue

            except ProfileIsPrivateError as desc:
                stacktrace = f'{desc}'
                self._error_handler(url, stacktrace)
                continue

            except Exception as desc:
                stacktrace = f'Failed -> {desc}'
                self._error_handler(url, stacktrace)
                continue

        self.driver.close()

        if len(self.logins) == len(self.channels_failed):
            raise MainError("total failed")

        return self.result_data

    def __collect_data(self, url) -> dict:
        logger.info('start collect data')
        html = self.driver.find_element(By.XPATH, "//html").get_attribute('innerHTML')
        data = dict()
        data['link'] = url
        data['body'] = self.get_body_info(html)
        data['date'] = self.get_post_time(self.driver)
        data['number_of_likes'] = self.get_number_of_likes(html)
        data['number_of_comments'] = self.get_number_of_comments(html)
        data['comments_data']: list = self.get_comments_data(self.driver)
        data['likers_data']: list = self.get_likers_data(self.driver)
        logger.info('finish collect data')
        return data


    def _error_handler(self, url, stacktrace):
        # self.channels_failed.append(url)
        # TaskStatus_(task_id=self.task_id,
        #             task_type=self.task_type,
        #             login=url).warning(change_asup=True, change_local=False)
        logger.error(stacktrace)




