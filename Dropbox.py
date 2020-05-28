import json
import sys
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\endpoint')

from endpoint.Endpoint import endpoint
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import tokenUtils


class dropbox(endpoint):
    def __init__(self):
        self.credentialId = ''
        self.dest = ''
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
        url = 'http://localhost:8080/api/dropbox/ls'
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

        url="http://localhost:8080/api/dropbox/mkdir"            
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

        url="http://localhost:8080/api/dropbox/rm"            
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
        url = 'http://localhost:8080/api/dropbox/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        if len(response['files']) == 0:
            print("No files Found")
        else :
            for file in response['files']:
                print(file['name'])
    
    def transfer(self,fileName)-> None:
        data={
                "src":{
                "credential":{
                        "uuid":self.credentialId,
                        "name":"Dropbox: bhaktij910@gmail.com",
                        "tokenSaved":True
            },
                "uri":"dropbox:///"+fileName,
                "type":"dropbox:///",
                "map":[{"id":None,"path":"dropbox:///"}]
            },
            
                "dest":{
                "credential":{
                        "uuid":self.dest,
                        "name":"Dropbox: bhaktij910@gmail.com",
                        "tokenSaved":True
            },
                "id":None,
                "uri":"googledrive:/"+fileName,
                "type":"googledrive:/",
                "map":[{"id":None,"path":"googledrive:/"}]
            },
            
        "options":{
            "optimizer":"None",
            "overwrite":True,
            "verify":True,
            "encrypt":True,
            "compress":True,
        "retry":5
            }	
        }
        
        
        url="http://localhost:8080/api/stork/submit"         
        request=endpoint._post_request(url, data,self.headers) 
        if(request.status_code==200):
            print('Success')

    def download(self, fileName) -> None:
        print(fileName)
        data={"uri":"dropbox:///"+fileName,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktij910@gmail.com",
                            "tokenSaved":True
                    },
              }

        url="http://localhost:8080/api/dropbox/download"            
        request=endpoint._post_request(url,data,self.headers)
        if(request.status_code==200):
            print('Success')

    def upload(self, payload) -> None:
        raise NotImplemented()

