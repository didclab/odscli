import requests

from onedatashare.endpoint.Endpoint import Endpoint


class Dropbox(Endpoint):
    def __init__(self, credentialId):
        self.credentialId = credentialId

    def list(self, payload) -> str:
        with requests.Session() as rs:
            response = self._post_request(url, data=json.dumps(data), headers=headers)

    def mkdir(self, payload) -> None:
        raise NotImplemented()

    def delete(self, payload) -> None:
        raise NotImplemented()

    def download(self, payload) -> None:
        raise NotImplemented()

    def upload(self, payload) -> None:
        raise NotImplemented()