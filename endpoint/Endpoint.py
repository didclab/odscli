import requests
import sys
import json
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import tokenUtils
from abc import ABC, abstractmethod


class endpoint(ABC):
    def __init__(self) -> 'endpoint':
        self.__headers = ''

    def _post_request(url, data, headers):
        return requests.Session().post(url = url, data = json.dumps(data), headers=headers)

    def _get_request(self, url, data):
        return requests.get(url = url, data = data)

    @abstractmethod
    def list(self) -> str:
        raise NotImplemented()

    @abstractmethod
    def mkdir(self, fileName) -> None:
        raise NotImplemented()

    @abstractmethod
    def delete(self, fileName) -> None:
        raise NotImplemented()

    @abstractmethod
    def download(self, payload) -> None:
        raise NotImplemented()

    @abstractmethod
    def upload(self, payload) -> None:
        raise NotImplemented()