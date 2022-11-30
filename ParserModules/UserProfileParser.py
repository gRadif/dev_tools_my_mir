import logging

# from api.management.Threads.manage_threads import Thread
# from api.service import TaskStatus_
# from api.service.service_exceptions import StopParserWork, ErrorOpenUrl
# from my_mail_ru_parser.DataContainers import ServiceData

# from my_mail_ru_parser.SaveParsedData.save_to_db_profile_data import ProfilesData
import time
from dataclasses import dataclass
from pprint import pprint

from ParserModules.BaseParser import BaseParser

logger = logging.getLogger(__name__)


class StopParserWork(BaseException):
    pass


@dataclass
class ServiceData:
    logins: tuple
    task_id: str
    free_thread_id: int
    task_type: str


# type 4
class UserProfileParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.urls: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type  # todo:

    def run(self):
        if self.auth_mail_ru():
            all_data = []
            for url in self.urls:
                data_container = {}
                try:
                    self.open_url(url)
                    self.open_url(url)

                    data_container["login"] = url
                    data_container["age"] = self.get_age(self.driver)
                    data_container["username"] = self.get_username(self.driver)
                    data_container["last_online"] = self.get_last_online(self.driver)
                    data_container["is_private"] = self.is_private(self.driver)
                    data_container["photo_url"] = self.take_user_profile_photo_url(self.driver)
                    data_container["number_of_friends"] = self.number_of_friends(self.driver)
                    data_container["number_of_photo"] = self.number_of_photo(self.driver)
                    data_container["number_of_video"] = self.number_of_video(self.driver)
                    data_container["number_of_music"] = self.number_of_music(self.driver)
                    data_container["number_of_groups"] = self.number_of_groups(self.driver)
                    data_container["number_of_games"] = self.number_of_games(self.driver)
                    all_data.append(data_container)

                except Exception as e:
                    # TaskStatus_(task_id=self.task_id,
                    #             task_type=self.task_type,
                    #             login=url).warning(change_asup=True, change_local=False)
                    logger.error(f'profile parser error -->> {e}')
                    continue

            self.driver.close()
            return all_data
        else:
            # TaskStatus_(task_id=self.task_id, error_name="Auth Error",
            #             error_description="attempting auth failed").error(change_asup=True, change_local=False)
            logger.debug('else block')

