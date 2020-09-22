import requests
import sys
import json
import tokenUtils as tokenUtils
from abc import ABC, abstractmethod
from enum import Enum
import constants

class EndpointType(Enum):
    SFTP = "sftp"
    FTP = "ftp"
    S3 = "s3"
    HTTP = "http"
class EndpointTypeOAUTH(Enum):
    BOX = "box"
    DROPBOX = "dropbox"
    GOOGLE_DRIVE = "gdrive"
    GFTP = "globus"

class endpoint():
    #Takes a string in and returns the type and boolean of isOAuth (str,bool)
    def type_handle(typeString:str):
        typeString = typeString.upper()
        try:
            return EndpointType[typeString].value,False
        except KeyError:
            try:
                return EndpointOAuth[typeString].value,True
            except:
                print("No Valid Type")
                raise
        except:
            print("Unknown Error")
            raise
    #OLD CODE ---- IGNORING FOR NOW
    #def _post_request(url, data, headers):
        #return requests.Session().post(url = url, data = json.dumps(data), headers=headers)

    #def _get_request(self, url, data):
        #return requests.get(url = url, data = data)

    #NEEDS TO BE IMPLEMENTED FOR SDK
    #def create(type:EndpointType,cred_id:str,ODS_AUTH_TOKEN:str):
        #raise NotImplemented()

    #@abstractmethod
    def list(remoteHost,path,identifier,host,type,atok) -> str:

        getreq = "http://"+host+":"+constants.PORT+constants.LISTV2
        reqForm = getreq.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'identifier':identifier}
        req = requests.get(reqForm,params=body,cookies=cookies)
        return req.text

    #@abstractmethod
    def mkdir(remoteHost, path, identifier, host, type, atok,dirToAdd) -> str:
        req = "http://"+host+":"+constants.PORT+constants.MKDIRV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'folderToCreate':dirToAdd}
        reqs = requests.post(reqForm,json=body,cookies=cookies)
        return reqs.text



    @abstractmethod
    def remove(self, fileName) -> bool:
        raise NotImplemented()

    @abstractmethod
    def download(self, payload) -> bool:
        raise NotImplemented()

    @abstractmethod
    def upload(self, payload) -> bool:
        raise NotImplemented()
