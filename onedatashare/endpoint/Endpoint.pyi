import requests
import utils.tokenUtils as tokenUtils
import utils.endpointUtils as endpointUtils
from abc import ABC, abstractmethod


class Endpoint(ABC):
    def __init__(self) -> 'Endpoint':
        self.__headers = {
            'Authorization': 'Bearer ' + tokenUtils.get_auth_token(),
            'content-type': 'application/json'
        }

    def _post_request(self, url, data, payload):
        return requests.post(url = url, data = data, payload = payload, headers=self.__headers)

    def _get_request(self, url, data):
        return requests.get(url = url, data = data)

    @abstractmethod
    def list(self, payload) -> str:
        raise NotImplemented()

    @abstractmethod
    def mkdir(self, payload) -> None:
        raise NotImplemented()

    @abstractmethod
    def delete(self, payload) -> None:
        raise NotImplemented()

    @abstractmethod
    def download(self, payload) -> None:
        raise NotImplemented()

    @abstractmethod
    def upload(self, payload) -> None:
        raise NotImplemented()