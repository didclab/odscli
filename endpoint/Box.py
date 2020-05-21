import json
import sys
import os
import urllib.request
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\endpoint')

from endpoint.Endpoint import endpoint
sys.path.insert(0, r'C:\Users\hardikck\.spyder-py3\cmdline\utils')

import tokenUtils


class box(endpoint):
    def __init__(self):
        self.credentialId = ''
        self.dest = ''
        self.headers = {
            'Authorization': 'Bearer ' + tokenUtils.get_ods_auth_token(),
            'content-type': 'application/json'
        }

    def list(self) -> str:
        data = {"uri":"box:///",
                "id":None,
                "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Box: bhaktiha@buffalo.edu.com",
                            "tokenSaved":True
                    }
                }
        url = 'http://localhost:8080/api/box/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        
        return response
    
    def printlist(self) -> str:
        
        response=box.list(self)
        for file in response['files']:
            print(file['name'])
            
    def mkdir(self, fileName) -> None:
        data={"uri":"box:///"+fileName,
              "id":None,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Box: bhaktiha@buffalo.edu.com",
                            "tokenSaved":True
                    },
              "map":[{"id":None,"path":"box:///"}]
              }
        

        url="http://localhost:8080/api/box/mkdir"            
        request=endpoint._post_request(url,data,self.headers)
        if(request.status_code==200):
            print('Success')

    def delete(self, fileName) -> None:
        response = box.list(self)
        id=''
        for file in response['files']:
            if(file['name']==fileName):
                id=file['id']
        
        data={"uri":"box:///"+fileName,
              "id": id,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Box: bhaktiha@buffalo.edu.com",
                            "tokenSaved":True
                    },
              "map":[{"id":None,"path":"box:///"}]
              }
        
        url="http://localhost:8080/api/box/rm"            
        request=endpoint._post_request(url,data,self.headers)
        if(request.status_code==200):
            print('Success')


    
    def folderfiles(self,fileName) -> None:
        response = box.list(self)
        id=''
        for file in response['files']:
            if(file['name']==fileName):
                id=file['id']
                
        data = {"uri":"box:///"+fileName,
                "id":id,
                "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Dropbox: bhaktiha@buffalo.edu",
                            "tokenSaved":True
                    }
                }
        url = 'http://localhost:8080/api/box/ls'
        request = endpoint._post_request(url, data,self.headers)
        response = json.loads(request.content)
        if len(response['files']) == 0:
            print("No files Found")
        else :
            for file in response['files']:
                print(file['name'])
    
    def transfer(self,fileName)-> None:
        raise NotImplemented()

    def download(self, fileName) -> None:

        response = box.list(self)
        id=''
        for file in response['files']:
            if(file['name']==fileName):
                id=file['id']
        
        data={"uri":"box:///"+fileName,
              "id" : id,
              "credential":
                    {
                            "uuid":self.credentialId,
                            "name":"Box: bhaktiha@buffalo.edu",
                            "tokenSaved":True
                    }
              }

        url="http://localhost:8080/api/box/download"            
        request=endpoint._post_request(url,data,self.headers)
        response = json.loads(request.content)
        download_folder = os.path.expanduser("~")+"/Downloads/"
        fullfilename = os.path.join(download_folder, fileName.rpartition('/')[2])
        urllib.request.urlretrieve(response,fullfilename)
        if(request.status_code==200):
            print('Success')       

    def upload(self, payload) -> None:
        raise NotImplemented()

   