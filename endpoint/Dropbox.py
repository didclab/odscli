import json
import sys
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\endpoint')

from endpoint.Endpoint import endpoint
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import tokenUtils


class dropbox(endpoint):
    def __init__(self):
        self.credentialId = ''
        self.headers = {
            'Authorization': 'Bearer ' + tokenUtils.get_ods_auth_token(),
            'content-type': 'application/json'
        }

    def list(self) -> str:
        data = {"uri":"dropbox:///",
                "id":None,
                "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktij910@gmail.com",
                            "tokenSaved":True
                    }
                }
        url = 'https://www.onedatashare.org/api/dropbox/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        for file in response['files']:
            print(file['name'])

    def mkdir(self, fileName) -> None:
        data={"uri":"dropbox:///"+fileName,
              "id":None,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktij910@gmail.com",
                            "tokenSaved":True
                    },
              "map":[{"id":None,"path":"dropbox:///"}]
              }

        url="https://www.onedatashare.org/api/dropbox/mkdir"            
        request=endpoint._post_request(url,data,self.headers)
        if(request.status_code==200):
            print('Success')

    def delete(self, fileName) -> None:
        data={"uri":"dropbox:///"+fileName,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktij910@gmail.com",
                            "tokenSaved":True
                    },
              "map":[{"id":None,"path":"dropbox:///"}]
              }

        url="https://www.onedatashare.org/api/dropbox/rm"            
        request=endpoint._post_request(url,data,self.headers)
        if(request.status_code==200):
            print('Success')
    
    def folderfiles(self,fileName) -> None:
        data = {"uri":"dropbox:///"+fileName,
                "id":None,
                "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktij910@gmail.com",
                            "tokenSaved":True
                    }
                }
        url = 'https://www.onedatashare.org/api/dropbox/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        if len(response['files']) == 0:
            print("No files Found")
        else :
            for file in response['files']:
                print(file['name'])
    
    def transfer(self,src,dest,fileName)-> None:
        raise NotImplemented()

    def download(self, payload) -> None:
        raise NotImplemented()

    def upload(self, payload) -> None:
        raise NotImplemented()

