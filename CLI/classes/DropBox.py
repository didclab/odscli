#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import json

class dropBox:

    def __init__(self):
        self.credential=''
        self.token=''

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
            print(response)
            for file in response['files']:
                print(file['name'])


    def mkdirDbx(self, credential, fileName):
        if not credential:
            credential = input('DropBox Account:')
        if not fileName:
            fileName = input('FileName:')

        data = {
            'credential': {'name': 'credential', 'tokenSaved': False,
                           'token': 'HcMXTiTtgesAAAAAAAAA4Qt-abaLywfk4d9-nmvSoFCAt4lJ3UED7IWTjkNdDNas'},
            'uri': 'dropbox:///' + fileName,
            'id': None,
            'map': [{'id': None, 'path': 'dropbox:///'}],
            }

        with requests.Session() as s:
            url = 'http://localhost:8080/api/dropbox/mkdir'
            req = s.post(url, data=json.dumps(data),
                         headers=self.headers)
            if(req.status_code == '200'):
                print('Status: Success')
