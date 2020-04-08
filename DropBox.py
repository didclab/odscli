#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json

class dropBox:

    def __init__(self):
        self.credential=''
        self.token=''
        self.fileName=''
        self.credential1=''
        self.credential2=''

    def getDbxList(self):
        
        headers={'content-type': 'application/json',
                 'Authorization': 'Bearer '+ self.token
                }
        data = {'uri': 'dropbox:///', 'id': None,
                'credential': {'name': self.credential, 'tokenSaved': False,
                'token': 'HcMXTiTtgesAAAAAAAACHbKdpwmsH9PNQYvNynU8ue37ystwSwYn4N6dZUfkqEQ2'}}

        with requests.Session() as s:
            url = 'http://localhost:8080/api/dropbox/ls'
            req = s.post(url, data=json.dumps(data),
                         headers=headers)
            response = json.loads(req.content)
            for file in response['files']:
                print(file['name'])


    def mkdirDbx(self):
        headers={'content-type': 'application/json',
                 'Authorization': 'Bearer '+ self.token
                }

        data = {
            'credential': {'name': self.credential, 'tokenSaved': False,
                           'token': 'HcMXTiTtgesAAAAAAAACHbKdpwmsH9PNQYvNynU8ue37ystwSwYn4N6dZUfkqEQ2'},
            'uri': 'dropbox:///' + self.fileName,
            'id': None,
            'map': [{'id': None, 'path': 'dropbox:///'}],
            }

        with requests.Session() as s:
            url = 'http://localhost:8080/api/dropbox/mkdir'
            req = s.post(url, data=json.dumps(data),
                         headers=headers)
            print(req.status_code)
            
    def folderlistDbx(self):
        headers={
        'content-type': 'application/json',
        'Authorization': 'Bearer '+self.token
        }
        
        data={
        
    	"credential":{
    		"name":self.credential,
    		"tokenSaved":False,
    		"token":"HcMXTiTtgesAAAAAAAAA4Qt-abaLywfk4d9-nmvSoFCAt4lJ3UED7IWTjkNdDNas"
            },
    		"uri":"dropbox:///"+self.fileName
    		
    
        }
        
        with requests.Session() as s:
            url="http://localhost:8080/api/dropbox/ls"         
            req=s.post(url,data=json.dumps(data),headers=headers)
            response=json.loads(req.content)
            if len(response['files']) == 0:
                print("No files Found")
            else :
                for file in response['files']:
                    print(file['name'])
                
                
    def deleteDbx(self):
        headers={
        'content-type': 'application/json',
        'Authorization': 'Bearer '+self.token
        }
        
        data={
        
    	"credential":{
    		"name":self.credential,
    		"tokenSaved":False,
    		"token":"HcMXTiTtgesAAAAAAAAA5s2ypub-9ClCuYEdLCgslxls5LQ99PznDc1KCZobV3D8"
            },
    		"uri":"dropbox:///"+self.fileName,
    		"map":[{
    			"id":None,
    			"path":"dropbox:///"}]
    		
        }
        
        with requests.Session() as s:
            url="http://localhost:8080/api/dropbox/rm"         
            req=s.post(url,data=json.dumps(data),headers=headers)
            print(req.status_code)
            
    def transferDbxtoGdrive(self):
        headers={
        'content-type': 'application/json',
        'Authorization': 'Bearer '+self.token
        }
        
        data={
        "src":{
        "credential":{
            "name":self.credential1,
            "tokenSaved":False,
            "token":"HcMXTiTtgesAAAAAAAACFnMD0RSHxIq98VikvWEqx-_-axXNz_RmfIaY6-KRnybW"
            },
            "uri":"dropbox:///"+self.fileName,
            "type":"dropbox:///",
            "map":[{"id":None,"path":"dropbox:///"}]
            },
            
        "dest":{
        "credential":{
            "name":self.credential2,
            "tokenSaved":False,
            "token":"ya29.a0Adw1xeV5xaBqlOx9HyXUKh7j9ILhOyyOCOjFa_C800UP5ElveYGvDpwQKDWU02DZ4yFI1JrCql_1I7IpIJ4nQBuRG9_YaJ6g95muminHkKFWqM-uAEWbWTlMnmOwEqMwF88cxqpd4zOEj34HsbLo1J_1v9DREvinAcg"},
            "id":None,
            "uri":"googledrive:/"+self.fileName,
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
        
        with requests.Session() as s:
            url="http://localhost:8080/api/stork/submit"         
            req=s.post(url,data=json.dumps(data),headers=headers)
            print(req.status_code)
