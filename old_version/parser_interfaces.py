import re
import logging
import pymysql as pymysql
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from my_mail_ru_microservice.my_mail_ru_parser.config import LIST_OF_DATE, host, port, user, password, database


def set_options_driver() -> webdriver:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})  # Disable notification
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable diver automation
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")  # Running in the background
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def get_post(driver, connection, url):
    post_info = {
        "resource": "Mailru",
        # "created_at": datetime.fromisoformat(set_time(driver.find_element_by_class_name(
        #     "b-comments__item-actions-date").text)).timestamp(),
        "created_at": datetime.now().timestamp(),
        "project_name": driver.find_element_by_class_name("b-history-event__ownername").text,
        "id_format_content": get_type_post(driver=driver),
        "name_content": driver.find_element_by_class_name("b-history-event__event-text-page ").text.split("\n")[0],
        "url_address": url,
        "success": 0,
        "success_date_update": datetime.now().timestamp(),
        "count_like": driver.find_element_by_class_name("b-like__button-counter__number").text
    }

    with connection.cursor() as cursor:
        insert = "INSERT INTO `content` (resource, created_at, project_name, id_format_content, name_content," \
                 "url, success, success_date_update) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (post_info["resource"], post_info["created_at"], post_info["project_name"],
               post_info["id_format_content"], post_info["name_content"], post_info["url_address"],
               post_info["success"], post_info["success_date_update"])
        cursor.execute(insert, val)
        connection.commit()
        cursor.execute("SELECT `id_content` FROM `content` WHERE url=%s", url)
        post_id = cursor.fetchone()["id_content"]
        add_metrics(connection=connection, post_info=post_info, post_id=post_id)
        return post_id


def add_metrics(connection, post_info, post_id):
    with connection.cursor() as cursor:
        insert = 'INSERT INTO `metrics` (material_id, id_metrics_name, value, time) VALUES (%s, %s, %s, %s)'
        val = (post_id, post_info["id_format_content"], post_info["count_like"], datetime.now().timestamp())
        cursor.execute(insert, val)
        connection.commit()
        return True


def get_type_post(driver):
    try:
        if driver.find_element_by_class_name("b-history-event__photoevent"):
            return 1
    except Exception:
        pass
    try:
        if driver.find_element_by_class_name("b-history-event__videoevent-object"):
            return 0
    except Exception:
        pass
    return 2


def load_comments(driver, url, connection):
    driver.get(url)
    logging.info(f"Start parsing: {url}")
    # load comments
    while True:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "b-comments__count"))).click()
        except Exception:
            break
    return get_comments(driver=driver, connection=connection)


def get_comments(driver, connection):
    try:
        messages = driver.find_elements_by_class_name("b-comments__item")
        all_comments = []
        for i in messages:
            if len(all_comments) >= 50:
                commit_database_message(all_comments=all_comments, connection=connection)
                all_comments.clear()
            all_comments.append(app(i))
        return commit_database_message(all_comments=all_comments, connection=connection)
    except Exception as e:
        logging.error(f"Exception: {e}")
        exit(1)


def app(i):
    try:
        res = {
            "comment_id": i.get_attribute("data-comment-id"),
            "user_id": i.get_attribute("author-id"),
            "name": i.find_element_by_class_name("b-comments__item-username").text,
            "comment": i.find_element_by_class_name("b-comments__item-text").text,
            "comment_original": i.find_element_by_class_name("b-comments__item-text").text,
            "like_count": 0 if i.find_element_by_class_name(
                "b-comments__item-actions-like__count").text == "" else i.find_element_by_class_name(
                "b-comments__item-actions-like__count").text,
            "published": set_time(i.find_element_by_class_name("b-comments__item-actions-date").text)
        }
        return res
    except Exception:
        pass


def set_time(_time):
    if "час" in _time:
        return datetime.timestamp(datetime.now() - timedelta(hours=int(re.search('\d+', _time).group(0))))
    if "минут" in _time:
        return datetime.timestamp(datetime.now() - timedelta(minutes=int(re.search('\d+', _time).group(0))))
    if "понедельник" in _time or "вторник" in _time or "сред" in _time or "четвер" in _time or "пятниц" in _time or \
            "суббот" in _time or "воскресе" in _time:
        return datetime.now().isoformat()
    try:
        return datetime(year=int(re.search('\d{4}', _time).group(0)),
                        month=int(LIST_OF_DATE[re.search('\w{3,}', _time).group(0)]),
                        day=int(re.search('\d+', _time).group(0)),
                        hour=int(re.findall('\d{2}', _time)[-2]),
                        minute=int(re.findall('\d{2}', _time)[-1])).isoformat()
    except Exception:
        return datetime(year=int(date.today().year),
                        month=int(LIST_OF_DATE[re.search('\w{3,}', _time).group(0)]),
                        day=int(re.search('\d+', _time).group(0)),
                        hour=int(re.findall('\d{2}', _time)[-2]),
                        minute=int(re.findall('\d{2}', _time)[-1])).isoformat()


def commit_database_message(all_comments, connection):
    with connection.cursor() as cursor:
        for i in range(len(all_comments)):
            if all_comments[i] is not None:
                insert = 'INSERT IGNORE INTO `comments` (comment_id, user_id, name, comment, comment_original, ' \
                         'like_count, published) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                val = (all_comments[i]['comment_id'], all_comments[i]['user_id'], all_comments[i]['name'],
                       all_comments[i]['comment'], all_comments[i]['comment_original'],
                       all_comments[i]['like_count'],
                       all_comments[i]['published'])
                cursor.execute(insert, val)
        connection.commit()


def main(parse_url):
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Successfully connection to database")
        logging.info("Parsing start")
        driver = set_options_driver()
        load_comments(driver=driver, url=parse_url, connection=connection)
        get_post(driver=driver, connection=connection, url=parse_url)
        logging.info("Parsing completed")
        logging.info("Close browser")
    except pymysql.err.OperationalError:
        logging.info("Unsuccessfully connection to database")
        exit(1)


def select_url() -> list[str]:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        logging.info("Select url")
        with connection.cursor() as cursor:
            cursor.execute("SELECT `url` FROM `content` WHERE resource='Mailru'")
            _urls = cursor.fetchall()
            urls = []
            if not _urls:
                logging.info("No links")
                return exit(1)
            for url in _urls:
                urls.append(url["url"])
            urls = list(set(urls))
            logging.info(f"Select {len(urls)} urls")
            return urls
    except pymysql.err.OperationalError:
        logging.error("Unsuccessfully connection to database")
        exit(1)


if __name__ == '__main__':
    urls = select_url()
    for url in urls:
        main(url)
