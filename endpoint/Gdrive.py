import json
import sys
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\endpoint')

from endpoint.Endpoint import endpoint
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import utils.tokenUtils as tokenUtils


class gdrive(endpoint):
    def __init__(self):
        self.credentialId = ''
        self.headers = {
            'Authorization': 'Bearer ' + tokenUtils.get_ods_auth_token(),
            'content-type': 'application/json'
        }

    def list(self) -> str:
        data = {"uri":"googledrive:/",
                "id":None,
                "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"GoogleDrive: bhaktij910@gmail.com",
                            "tokenSaved":True
                    }
                }
        url = 'http://localhost:8080/api/googledrive/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        for file in response['files']:
            print(file['name'])
            
    def mkdir(self, fileName) -> None:
        raise NotImplemented()

    def delete(self, fileName) -> None:
        raise NotImplemented()
    
    def transfer(self,src,dest,fileName)-> None:
        raise NotImplemented()

    def download(self, payload) -> None:
        raise NotImplemented()

    def upload(self, payload) -> None:
        raise NotImplemented()