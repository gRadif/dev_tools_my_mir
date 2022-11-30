import hashlib
from hashlib import md5

import requests



class MyMailApi:
    BaseUrl = 'http://www.appsmail.ru/platform/api'
    app_id = 786782
    private_key = "8c6a3a122a8190eb8e9e0013b56847ff"

    def __init__(self):
        self.sig = None


    def get_profile_info(self):
        self.__get_hash_md5()
        headers = {'app_id': f"{self.app_id}",
                    'sig': f"{self.sig}",
                    'method': 'users.getInfo',
                    'uid': f"{15854372461764008671}",
                    'secure': "1"}
        response = requests.get(url=self.BaseUrl, params=headers)
        print(response.json())

    def __get_hash_md5(self):
        string = ("15854372461764008671" + '920ee1ecdc187c3c1c2e68353c90dc19').encode()
        self.sig = hashlib.md5(string)
        print(self.sig)

if __name__ == '__main__':
    MyMailApi().get_profile_info()


'''Пусть uid=1324730981306483817 и secret_key=3dad9cbf9baaa0360c0f2ba372d25716

Запрос, который вы хотите выполнить:
http://www.appsmail.ru/platform/api?method=friends.get&app_id=423004&session_key=be6ef89965d58e56dec21acb9b62bdaa&secure=1

Тогда:
params = app_id=423004
method=friends.get
secure=1
session_key=be6ef89965d58e56dec21acb9b62bdaa
sig = md5(app_id=423004
method=friends.get
secure=1
session_key=be6ef89965d58e56dec21acb9b62bdaa3dad9cbf9baaa0360c0f2ba372d25716)
    = 4a05af66f80da18b308fa7e536912bae

Итоговый запрос:
http://www.appsmail.ru/platform/api?method=friends.get&app_id=423004&session_key=be6ef89965d58e56dec21acb9b62bdaa&secure=1&sig=4a05af66f80da18b308fa7e536912bae
'''