import requests


class Notify:
    def __init__(self):
        self.__base_url = 'https://webhook.site/74700838-c709-4682-a339-fbeedcf549c8'

    def send_notification(self, transaction):
        requests.post(
            url=self.__base_url,
            json=transaction,
            )
