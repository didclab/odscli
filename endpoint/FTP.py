import json
import sys
from endpoint.Endpoint import endpoint
import utils.tokenUtils as tokenUtils


class ftp(endpoint):
    def __init__(self):
        self.credentialId = ''
        self.headers = {
            'Authorization': 'Bearer ' + tokenUtils.get_ods_auth_token(),
            'content-type': 'application/json'
        }

    def list(self) -> str:
        raise NotImplemented()

    def mkdir(self, fileName) -> None:
        raise NotImplemented()

    def delete(self, fileName) -> bool:
        raise NotImplemented()

    def transfer(self, src, dest, fileName) -> None:
        raise NotImplemented()

    def download(self, payload) -> None:
        raise NotImplemented()

    def upload(self, payload) -> None:
        raise NotImplemented()
