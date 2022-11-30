import logging
import time

from ParserModules.BaseParser import BaseParser, ErrorOpenUrl
from ParserModules.UserProfileParser import ServiceData
from service_exeptions import AuthorizationError

logger = logging.getLogger("debug")


class VideoParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.urls: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type  # todo:
        self.video_data = []

    def launch(self):
        try:
            self.auth_mail_ru()
            logger.info(f'number of input logins -> {len(self.urls)}')
            for url in self.urls:
                self.open_url(url)
                self.checking_page_not_found()
                # self.checking_private_page()
                # time.sleep(1000)
                self.video_data.append(self.__get_data(url))
                # time.sleep(10000)


        except ErrorOpenUrl as err:
            logger.error("ErrorOpenUrl", exc_info=True)

        except AuthorizationError as err:
            logger.error("AuthorizationError", exc_info=True)
        print(self.video_data)
        time.sleep(1000)
        return self.video_data

    def __get_data(self, url):
        data = {}
        first_video_tag = self.get_first_video_tag(self.driver)
        data['link'] = url
        data['title'] = self.get_title(first_video_tag)
        data['views'] = self.get_video_views(first_video_tag)
        data['date'] = self.get_video_date(first_video_tag)
        data['number_of_likes'] = self.get_video_number_of_likes(first_video_tag)
        data['number_of_comments'] = self.get_video_number_of_comments(first_video_tag)

        if data['number_of_comments'] != "None":
            data['comments'] = self.get_video_comments_data(first_video_tag)

        if data['number_of_likes'] != "None":
            data['likers'] = self.get_video_likers(first_video_tag, self.driver)

        return data
