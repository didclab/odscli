import json
import sys

sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\endpoint')

from endpoint.Endpoint import endpoint

sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import utils.tokenUtils as tokenUtils


class gridftp(endpoint):
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

    def delete(self, fileName) -> None:
        raise NotImplemented()

    def transfer(self, src, dest, fileName) -> None:
        raise NotImplemented()

    def download(self, payload) -> None:
        raise NotImplemented()

    def upload(self, payload) -> None:
        raise NotImplemented()
