import logging
from ParserModules.BaseParser import BaseParser
from ParserModules.UserProfileParser import ServiceData


logger = logging.getLogger(__name__)


class ChannelPostsParser(BaseParser):
    def __init__(self, service_data: ServiceData):
        super().__init__()
        self.urls: tuple = service_data.logins
        self.task_id: str = service_data.task_id
        self.free_thread_id: int = service_data.free_thread_id
        self.task_type = service_data.task_type  # todo:

    def get_data(self):
        self.auth_mail_ru()
        all_data = []

        for url in self.urls:
            if self.__check_url_is_valid(url) is False:
                continue
            self.open_url(url)

            data: list = self.__get_data()
            self.save_cookie()
            data_dict = {"url": url,
                         "data": data}

            for x in data_dict["data"]:
                print(x)
            all_data.append(data_dict)

        self.driver.close()
        return all_data


    def __get_data(self):
        data_list = []
        counter_button_down = 0
        post_links = set()
        while True:
            current_length_post_links = len(post_links)
            tags = self.get_posts_tags(self.driver)
            number_of_tags = len(tags)
            print(f'number_of_tags -> {number_of_tags}')
            for tag in list(tags):
                html = self.get_html_from_tag(tag)
                link = self.get_post_link(html)
                # todo: prepare link
                if link != "None":
                    if link in post_links:
                        continue
                    post_links.add(link)
                    data_container = {}
                    data_container['post_link'] = link
                    data_container['number_of_likes'] = self.get_number_of_likes(html)
                    data_container['number_of_comments'] = self.get_number_of_comments(html)
                    data_container['body'] = self.get_body_info(html)
                    data_container['date'] = self.get_post_time(html)
                    data_list.append(data_container)
                    print(f"length data list = {len(data_list)}")
                else:
                    continue

            self.click_down()
            if counter_button_down > 20:
                break
            else:
                pass

            if len(post_links) == current_length_post_links:
                counter_button_down += 1
            elif len(post_links) != current_length_post_links:
                counter_button_down = 0
            else:
                pass

        return data_list

    def __check_url_is_valid(self, url):
        profile_type = self.define_profile_type(url)
        if self.task_type == "12":
            if profile_type == "user":
                logger.warning('task type = 12, but url is user, this is error condition')
                return 1
            return 0
        else:
            logger.warning('task type is 11, but must have 12')
            return 0



