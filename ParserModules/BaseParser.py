import pickle
import time
from pprint import pprint

from django.conf import settings
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome import webdriver
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
import re
import logging
# from django.conf import settings
from selenium_stealth import stealth

from service_exeptions import AuthorizationError


class PageNotFoundError(BaseException):
    pass


class ProfileIsPrivateError(BaseException):
    pass

class ErrorOpenUrl(BaseException):
    pass


class ErrorClickLogIn(BaseException):
    pass


class StopParsing(BaseException):
    pass


account_username = 'rudolf_psp'
account_password = 'MAEPs2_ryyr3'

logging.basicConfig(format=u'[%(levelname)-s] [%(asctime)s] [LINE:%(lineno)d] - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
# logger = logging.getLogger("debug")


class Driver:

    # chrome_path = settings.CHROMEDRIVER
    chrome_path = os.path.join(os.getcwd(), 'chromedriver.exe')

    def __init__(self):
        self.driver = self.initialize_driver()

    def initialize_driver(self) -> webdriver:
        # proxy
        options = webdriver.ChromeOptions()
        # mobile_emulation = {
        #     "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        #     "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
        # options.add_experimental_option(
        #     "mobileEmulation", mobile_emulation)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2})  # Disable notification
        options.add_argument("--disable-blink-features=AutomationControlled")  # Disable diver automation
        options.add_argument('--no-sandbox')
        # options.add_argument("--headless")  # Running in the background
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument(f"user-data-dir={os.getcwd()}/cookies")
        options.add_argument('--log-level=3')
        logger.debug(f'chromedriver path -> {self.chrome_path}')
        driver: webdriver = webdriver.Chrome(executable_path=self.chrome_path, options=options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        logger.info('driver is initialized')
        return driver

    def save_cookie(self):
        cookie = self.driver.get_cookies()
        pickle.dump(cookie, open('session', 'wb'))
        logger.info('cookies is saved')

    def add_cookies(self):
        for cookie in pickle.load(open('session', 'rb')):
            self.driver.add_cookie(cookie)
        logger.info("cookies is loaded")

    def click_down(self):
        hook = self.driver.find_element(By.XPATH, "//html")
        hook.send_keys(Keys.END)


# type 2
class CollectorUserCommentsAndLikes:
    @staticmethod
    def get_user_posts_tags(driver):
        tags = driver.find_elements(By.XPATH, '//div[@id="history_container"]//div[contains(@class, "b-history-event  b-history-double-event ui-simple-block")]')
        return tags

    @staticmethod
    def get_comments_data(driver: webdriver) -> list:  # new method
        '''
        collected from current page all comments data
        '''
        counter = 0
        all_comments_tags = 0
        try:
            comments_count = int(driver.find_element(By.XPATH, '//span[@class="b-comments__count"]//span').text)
            logger.debug(f'number of comments ->> {comments_count}')
        except:
            logger.warning('not found number of comments')
            return []

        while True:
            try:
                time.sleep(2)
                try:
                    comment_load = driver.find_element(By.XPATH, '//span[@class="b-comments__count"]')
                    comment_load.click()
                except:
                    comment_load = driver.find_element(By.XPATH, '//span[@class="b-comments__count loaded"]')
                    comment_load.click()

                all_comments_tags = len(tuple(driver.find_elements(By.XPATH, '//div[@class="b-comments__item "]')))
                counter = 0
            except:
                counter += 1
                if counter > 3 and all_comments_tags > comments_count - 100:
                    logger.debug('stop cycle')
                    break

        all_comments_tags = driver.find_elements(By.XPATH, '//div[@class="b-comments__item "]')
        comments_container = []
        for iter, comment_tag in enumerate(all_comments_tags):
            try:
                data = dict()
                soup = BeautifulSoup(comment_tag.get_attribute('innerHTML'), "html.parser")
                data['sender_name'] = soup.find("div", class_="b-comments__item-username").find('a').get_text()
                data['sender_link'] = soup.find("div", class_="b-comments__item-username").find('a').get("href")
                try:
                    data['date'] = soup.find('div', class_='b-comments__item-actions-date').get_text()
                except:
                    data['date'] = "None"

                try:
                    data['text'] = soup.find('div', class_='b-comments__item-text').get_text()
                except:
                    data['text'] = "None"
                data['sum_id'] = f"{data['sender_name']}+{data['sender_link']}+{data['date']}"  # sum all value data
                comments_container.append(data)

            except:
                print('error in got info')
                continue
        print(f"comments collected ->> {len(comments_container)}")
        return comments_container

    @staticmethod
    def get_likers_data(driver: webdriver) -> list:
        logger.debug('start collecting likers data')
        try:
            button_like = driver.find_element(By.CLASS_NAME, "b-like__button-icon_liked")
            hover = ActionChains(driver).move_to_element(button_like)
            hover.perform()
            time.sleep(5)
            logger.debug("moved cursor")
            time.sleep(1)
            likers_list = driver.find_element(By.CLASS_NAME, "b-like__users-popuplink")
            likers_list.click()
        except:   # todo: will need defining error type
            time.sleep(2)
            logger.debug("moved cursor")
            time.sleep(1)
            try:
                likers_list = driver.find_element(By.CLASS_NAME, "b-like__users-popuplink")
                likers_list.click()
            except:
                try:
                    likers_list = driver.find_element(By.XPATH, "//span[@data-type='showlikers']")
                    likers_list.click()
                except:
                    return []
        logger.debug('likers field clicked')

        likers_data = []
        likers_links = set()
        time.sleep(3)
        try:
            likers = driver.find_elements(By.CLASS_NAME, "b-like__likers-item")
        except:
            return []
        for tag in likers:
            try:
                data = dict()
                soup = BeautifulSoup(tag.get_attribute('innerHTML'), 'html.parser')
                data['link'] = soup.find('a').get('href')
                if data['link'] in likers_links:
                    continue

                data['name'] = soup.find('a').get_text()
                likers_data.append(data)
                likers_links.add(data["link"])
            except:
                logger.debug("not found liker data")
        logger.debug(f"number of likers -> {len(likers_data)}")
        return likers_data


# type 3
class CollectorUserFriends:
    @staticmethod
    def get_friends_tags(driver):
        innerHTML = driver.find_element(By.XPATH, "//html").get_attribute('innerHTML')
        soup = BeautifulSoup(innerHTML, "html.parser")
        friends_tags = soup.find_all('ul', class_='b-catalog__friends-item')
        return friends_tags

    @staticmethod
    def get_friend_link(soup):
        try:
            # soup = BeautifulSoup(html, 'html.parser')
            friend_tag = soup.find('span', class_='b-catalog__friends-item-right-block b-catalog__friends-item-right-block-name').find('a')
            link = friend_tag.get('href')
            if link is not None:
                link = "https://my.mail" + link
            name = friend_tag.get_text(separator=" ", strip=True)

            return link, name
        except Exception as desc:
            print(f'error in get friend link -> {desc}')
            return "None", "None"

    @staticmethod
    def get_html(tag: webelement):
        html = tag.get_attribute('innerHTML')
        return html


# type 5
class CollectorChannelFollowers:
    @staticmethod
    def get_channel_followers(driver) -> list[dict]:
        '''
        collected followers tags from page
        :param driver:
        :return: user data, name and link
        '''
        data = []
        try:
            friends_tags = driver.find_elements(By.XPATH, '//div[@class="person h-155"]')
        except:
            time.sleep(5)  # WebDriverWait is not work
            try:
                friends_tags = driver.find_elements(By.XPATH, '//div[@class="person h-155"]')
            except:
                return data
        for tag in friends_tags:
            html = tag.get_attribute('innerHTML')
            soup = BeautifulSoup(html, 'lxml')
            link = soup.find('div', class_="name_pt").find('a').get('href')
            name = soup.find('div', class_="name_pt").find('a').get_text()
            data.append({
                'link': 'https://my.mail.ru' + link,
                'name': name
            })
        return data


# type 4
class CollectorUserProfileData:

    @staticmethod
    def take_user_profile_photo_url(driver) -> str:
        try:
            photo_url = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__avatarBlock"]//a')))
            photo_url = photo_url.get_attribute('href')
            logger.debug('photo_url is got')
            return photo_url

        except Exception as e:
            logger.warning(f'User profile photo is NOT taked')
            if settings.DEBUG:
                logger.warning(f'error description -> {e}')
            logger.debug('photo_url is not found')
            return "None"

    @staticmethod
    def get_age(driver) -> str:
        try:
            tag_age = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="profileContent"]/div/div[2]/span')))
            age = tag_age.text
            if age == ('', " "):
                logger.debug('age field is empty')
                return "None"
            logger.debug('age field is found')
            if isinstance(age, int):
                age = str(age)
            return age
        except:
            logger.debug("age field is not found")
            return "None"

    @staticmethod
    def get_username(driver):
        try:
            tag_username = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="profileCover"]//h1')))
            username = tag_username.text
            logger.debug("username is found")
            return username
        except:
            logger.debug("username is not found")
            return "None"

    @staticmethod
    def get_last_online(driver):
        try:
            tag_last_online = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@id="profileCover"]//span[1]')))
            last_online = tag_last_online.text
            logger.debug("last_online is found")
            return last_online

        except:
            logger.debug("last_online is not found")
            return "None"

    @staticmethod
    def is_private(driver) -> bool:
        """
        defining user is private or no
        :param driver:
        :return: bool
        """
        try:
            menu_tag = WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                                (By.XPATH, '//*[@class="b-user-main-page__feed"]')))
        except:
            return False
        if menu_tag.text.__contains__("Access restricted") or menu_tag.text.__contains__("Доступ ограничен"):
            return True

        logger.info('user profile is public')
        return False

    @staticmethod
    def number_of_friends(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                                    (By.XPATH, '//div[@class="profile__menu"]/a[2]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("number_of_friends is found")
            return number_of_friends

        except Exception as desc:
            logger.debug(f'dont get number of friends')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def number_of_photo(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__menu"]/a[3]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("number of photo is found")
            return number_of_friends

        except Exception as desc:
            logger.debug(f'dont get number of photo')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def number_of_video(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__menu"]/a[4]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("numner of video is found")
            return number_of_friends

        except Exception as desc:
            logger.debug(f'dont get number of video')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def number_of_music(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__menu"]/a[5]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("number of music is found")
            return number_of_friends

        except Exception as desc:
            logger.debug('dont get number of music')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def number_of_groups(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__menu"]/a[6]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("number of groups is found")
            return number_of_friends

        except Exception as desc:
            logger.debug(f'dont get number of groups')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def number_of_games(driver) -> str:
        try:
            tag_friends = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="profile__menu"]/a[7]/span[@class="profile__menuLinkCounter"]')))
            number_of_friends: str = tag_friends.text
            logger.debug("number_of_games is found")
            return number_of_friends

        except Exception as desc:
            logger.warning('dont get number of games')
            if settings.DEBUG:
                logger.warning(f'error description -> {desc}')
            return "None"

    @staticmethod
    def get_education(driver):
        return "None"

    @staticmethod
    def get_info_about_user(driver):
        return "None"

    @staticmethod
    def get_birthday(driver):
        try:
            tag_birthday = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(text(), "День рождения")]/../dd[2]')))
            location_info = tag_birthday.text
            return location_info
        except:
            return "None"

    @staticmethod
    def get_user_location(driver):
        try:
            tag_location = WebDriverWait(driver, 1).until(EC.presence_of_element_located(
                (By.XPATH, '//*[contains(text(), "Живу сейчас")]/..')))
            location_info = tag_location.text
            return location_info
        except:
            return "None"


class CollectorUserPosts:
    @staticmethod
    def get_user_posts(driver):
        tags = driver.find_elements(By.XPATH,
                                    '//div[@id="history_container"]//div[contains(@class, "b-history-event  ")]')
        return tags

    @staticmethod
    def take_body_post(html):
        pass


class CollectorVideoData:
    @staticmethod
    def get_first_video_tag(driver):
        video_tag = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.XPATH, '//div[@class="b-common__section b-video__section__item-page-player init"][1]')))
        return video_tag

    @staticmethod
    def get_title(video_tag: webelement):
        try:
            title = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__title").text
            logger.debug(f'title -> {title}')
        except Exception as err:
            title = "None"
            logger.error(f'get title error, desc: {err}')
        return title

    @staticmethod
    def get_video_views(video_tag: webelement):
        try:
            views = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__info__views").text
            logger.debug(f'views -> {views}')
        except Exception as err:
            views = "None"
            logger.error(f'{err}')
        return views

    @staticmethod
    def get_video_date(video_tag: webelement):
        try:
            date = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__info__date").text
            logger.debug(f'date -> {date}')
        except Exception as err:
            date = "None"
            logger.error(f'{err}')
        return date

    @staticmethod
    def get_video_number_of_likes(video_tag: webelement):
        try:
            number_of_likes = video_tag.find_element(By.CLASS_NAME, "b-like__button-counter__number").text
            logger.debug(f'number_of_likes -> {number_of_likes}')
        except Exception as err:
            number_of_likes = "None"
            logger.error(f'{err}')
        return number_of_likes

    def get_video_likers(self, video_tag: webelement, driver) -> list:
        likers_data = []
        likers_button = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__actions__like")
        hover = ActionChains(driver).move_to_element(likers_button)
        hover.perform()

        time.sleep(2)
        try:
            likers_list_button = video_tag.find_element(By.CLASS_NAME, "b-like__users-popuplink")
            likers_list_button.click()
            time.sleep(2)
        except Exception as err:
            logger.error(err)
            likers_count = self.get_video_number_of_likes(video_tag)
            if likers_count != "None":
                number_of_likers = int(likers_count)
                likers = video_tag.find_elements(By.XPATH, "//div[@class='avatar-container  b-like__avatar-container']//a")

                for x in range(number_of_likers):
                    data = {}
                    data['link'] = likers[x].get_attribute('href')
                    data['name'] = likers[x].get_attribute('title')
                    likers_data.append(data)
                return likers_data

        likers_list = driver.find_elements(By.CLASS_NAME, 'b-like__likers-item')
        for liker_tag in likers_list:
            data = {}
            data['name'] = self.__get_liker_name(liker_tag)
            data['link'] = self.__get_liker_link(liker_tag)
            likers_data.append(data)
        return likers_data

    def __get_liker_name(self, liker_tag: webelement):
        try:
            liker_name = liker_tag.find_element(By.XPATH, "//a").text
            logger.info(f'liker_name -> {liker_name}')
        except Exception as err:
            liker_name = "None"
            logger.error(f'liker name error -> {err}')
        return liker_name

    def __get_liker_link(self, liker_tag: webelement):
        try:
            liker_link = liker_tag.find_element(By.CLASS_NAME, "b-like__likers-item-name booster-sc").get_attribute('href')
            logger.info(f'liker_name -> {liker_link}')
        except Exception as err:
            liker_link = "None"
            logger.error(f'liker name error -> {err}')
        return liker_link

    @ staticmethod
    def get_video_number_of_comments(video_tag: webelement):
        try:
            number_of_comments = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__actions__button__count").text
            logger.debug(f'number_of_comments -> {number_of_comments}')
        except Exception as err:
            number_of_comments = "None"
            logger.error(f'{err}')
        return number_of_comments

    def get_video_comments_data(self, video_tag: webelement) -> list:
        comments_data = []
        button_comments = video_tag.find_element(By.CLASS_NAME, "sp-video__item-page-new__actions__button__icon")
        button_comments.click()
        time.sleep(2)

        comments_tags = video_tag.find_elements(By.CLASS_NAME, "b-comments__item")
        for comment_tag in comments_tags:
            data = {}
            data['commentator_link'] = self.__get_commentator_link(comment_tag)
            data['commentator_name'] = self.__get_commentator_name(comment_tag)
            data['text'] = self.__get_comment_text(comment_tag)
            data['date'] = self.__get_comment_date(comment_tag)
            data['sum_values'] = f'{data["comments_data"]}{data["commentator_name"]}{data["text"]}{data["date"]}'
            comments_data.append(data)

        return comments_data

    def __get_commentator_link(self, comment_tag: webelement):
        try:
            commentator_link = comment_tag.find_element(By.XPATH, "//div[@class='b-comments__item-username']//a").get_attribute('href')
            logger.debug(f'commentator_link -> {commentator_link}')
        except Exception as err:
            commentator_link = "None"
            logger.error(f'{err}')
        return commentator_link

    def __get_commentator_name(self, comment_tag: webelement):
        try:
            commentator_name = comment_tag.find_element(By.CLASS_NAME, "b-comments__item-username").text
            logger.debug(f'commentator_name -> {commentator_name}')
        except Exception as err:
            commentator_name = "None"
            logger.error(f'{err}')
        return commentator_name

    def __get_comment_text(self, comment_tag: webelement):
        try:
            comment_text = comment_tag.find_element(By.CLASS_NAME, 'b-comments__item-text').text
            logger.debug(f'comment_text -> {comment_text}')
        except Exception as err:
            comment_text = "None"
            logger.error(f'{err}')
        return comment_text

    def __get_comment_date(self, comment_tag: webelement):
        try:
            comment_date = comment_tag.find_element(By.CLASS_NAME, "b-comments__item-actions-date").text
            logger.debug(f'comment_date -> {comment_date}')
        except Exception as err:
            comment_date = "None"
            logger.error(f'{err}')
        return comment_date


class CollectorWallBodyInformation:
    '''
    for user and channel a wall
    '''
    @staticmethod
    def get_posts_tags(driver):
        tags = driver.find_elements(By.XPATH, '//div[@id="history_container"]//div[contains(@class, "b-history-event  ")]')
        return tags

    @staticmethod
    def get_html_from_tag(instance_selenium):
        html = instance_selenium.get_attribute('innerHTML')
        return html

    @staticmethod
    def get_post_link(html):
        link = "None"
        try:
            soup = BeautifulSoup(html, 'html.parser')
            time_tags = soup.find_all("div", class_="b-history-event_time")
            for time_tag in time_tags:
                try:
                    link = time_tag.find("a").get('href')
                    break
                except:
                    continue

            if link != "None":
                link = CollectorWallBodyInformation.prepare_post_link(link)
            return link
        except:
            return "None"

    @staticmethod
    def get_post_time(html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            date_time: str = soup.find("div", class_="b-history-event_time").find("a").get_text()
            date_time = date_time.replace('\t', '').replace('\n', '')
            return date_time
        except:
            return "None"

    @staticmethod
    def get_number_of_likes(html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            number_of_likes = soup.find("span", class_="b-like__button-counter__number").get_text()
            print(f'number_of_likes -> {number_of_likes}')
            if number_of_likes == "" or number_of_likes == " ":
                print('bad1')
                number_of_likes = "None"
            return number_of_likes
        except:
            print('bad2')
            return "None"

    @staticmethod
    def get_number_of_comments(html):
        try:
            logger.debug('getting number of comments')
            soup = BeautifulSoup(html, 'html.parser')
            number_of_comment = soup.find("span", class_="b-comments__history-button__number")
            number_of_comment = number_of_comment.get_text()
            if number_of_comment == "" or number_of_comment == " ":
                number_of_comment = "None"
            logger.info(f'got number -> {number_of_comment}')
            return number_of_comment
        except Exception as e:
            logger.error(f'error get number_of_comments -> {e}')
            return "None"
    # @staticmethod
    # def get_number_of_comments(html):
    #     try:
    #         soup = BeautifulSoup(html, 'html.parser')
    #         number_of_comment = soup.find("span", class_="b-comments__history-button__number")
    #         number_of_comment = number_of_comment.get_text()
    #         if number_of_comment == "" or number_of_comment == " ":
    #             number_of_comment = "None"
    #         return number_of_comment
    #     except:
    #         return "None"

    @staticmethod
    def get_body_info(html):
        body = "None"
        soup = BeautifulSoup(html, "html.parser")

        if soup.find("div", class_="b-history-event  b-history-double-event ui-simple-block stat-groups") is not None:
            print('THIS IS REPOST')

        try:
            text = soup.find('div', class_="b-history-event__event-textbox2").get_text().replace("\t", "").replace("\n", "")
            body = text
            return body
        except:
            pass

        try:
            image_link = soup.find('a', type="photolayer")
            body = image_link.get("href")
            return body
        except:
            pass

        try:
            music = soup.find("a", class_="jp__track-fullname-link").get('href')
            body = music
            return body
        except:
            pass

        return body

    @staticmethod
    def prepare_post_link(link) -> str:
        for i in range(len(link)):
            if link[i] == "?":
                link = "https://my.mail.ru" + link[:i]
                return link


class BaseParser(Driver, CollectorUserProfileData, CollectorWallBodyInformation, CollectorUserPosts, CollectorUserCommentsAndLikes, CollectorUserFriends, CollectorChannelFollowers, CollectorVideoData):
    '''
    по условию задачи может приходить логины только каналов или только пользователей
    '''


    def __init__(self):
        super().__init__()

    def auth_mail_ru(self):
        try:
            self.open_url(
                'https://account.mail.ru/login/?mode=simple&v=2.9.2&account_host=account.mail.ru&type=login&vk=1&ok=1&fb=1&app_id_mytracker=undefined&project=moymir&from=navi&success_redirect=https%3A%2F%2Fmy.mail.ru%2Fcommunity%2Fhigh_technology%2F%3Fref%3Dsrch&parent_url=https%3A%2F%2Fmy.mail.ru%2Fcommunity%2Fhigh_technology%2F%3Fref%3Dsrch')
            self.__to_input_auth_data()
            self.__click_sign_in()
            return True
        except Exception as err:
            raise AuthorizationError(f'{err}')

    def open_url(self, url):
        try:
            self.driver.get(url)
            logger.info(f'url opened -> {url}')
        except Exception as error:
            logger.error(f'not opened url = {url}, error info = {error}')
            raise ErrorOpenUrl(f'not opened url = {url}, error info = {error}')

    def define_profile_type(self, url: str):
        # https://my.mail.ru/community/android-apps/?ref=
        # https://my.mail.ru/mail/akulovdv/

        if url.__contains__("my.mail.ru/community/"):
            return "channel"
        elif url.__contains__("my.mail.ru/mail/"):
            return "user"
        else:
            # # for debug
            # if settings.DEBUG:
            #     raise
            # else:
            pass

    def switch_to_friends_page(self, driver, url):
        friends_url = url + '/friends'
        driver.get(friends_url)
        logger.info('friends page is opened')

    def checking_page_not_found(self):
        html: webelement = self.driver.find_element(By.XPATH, "//html").get_attribute('innerHTML')
        html: str = str(html)
        if html.__contains__('page not found') or html.__contains__('Page not found'):
            raise PageNotFoundError()

    def checking_private_page(self):
        html: webelement = self.driver.find_element(By.XPATH, "//html").get_attribute('innerHTML')
        html: str = str(html)
        if html.__contains__('profile') and html.__contains__('private'):
            raise ProfileIsPrivateError('profile is private')

    def __to_input_auth_data(self):
        time.sleep(5)
        username_fields = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))
        username_fields.send_keys(account_username)
        self.__click_button_enter_password()
        time.sleep(5)
        # password_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
        #                         (By.XPATH, '//div/input[@name="password"]')))

        password_field = self.driver.find_element(By.XPATH, '//div/input[@name="password"]')
        password_field.send_keys(account_password)

    def __click_button_enter_password(self):
        button_enter_password = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                                (By.XPATH, '//button/span[contains(text(), "Enter password")]')))
        time.sleep(1)
        button_enter_password.click()

    def __click_sign_in(self):
        button_sign_in = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//button/span[contains(text(), "Sign in")]')))
        button_sign_in.click()
        time.sleep(8)


