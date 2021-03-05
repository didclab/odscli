import requests
import json
import SDK.token_utils as tokenUtils
from abc import ABC, abstractmethod
from enum import Enum
import SDK.constants as constants

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

class Endpoint():
    #NEEDS TO BE IMPLEMENTED FOR SDK
    #def create(type:EndpointType,cred_id:str,ODS_AUTH_TOKEN:str):
        #raise NotImplemented()
    #Takes a string in and returns the type and boolean of isOAuth (str,bool)
    def type_handle(typeString:str):
        typeString = typeString.upper()
        try:
            return EndpointType[typeString].value,False
        except KeyError:
            try:
                return EndpointTypeOAUTH[typeString].value,True
            except:
                print("No Valid Type")
                raise
        except:
            print("Unknown Error")
            raise

    def list(remoteHost,path,identifier,host,type,atok) -> str:
        req = "http://"+host+":"+constants.PORT+constants.LISTV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'identifier':identifier}
        req = requests.get(reqForm,params=body,cookies=cookies)
        return req.text

    def mkdir(remoteHost, path, identifier, host, type, atok,dirToAdd) -> str:
        req = "http://"+host+":"+constants.PORT+constants.MKDIRV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'folderToCreate':dirToAdd}
        reqs = requests.post(reqForm,json=body,cookies=cookies)
        return reqs.text

    def remove(remoteHost, path, identifier, host, type, atok,filename) -> str:
        req = "http://"+host+":"+constants.PORT+constants.REMOVEV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'toDelete':filename}
        reqs = requests.post(reqForm,json=body,cookies=cookies)
        return req

    def download(remoteHost, path, identifier, host, type, atok,filename) -> str:
        req = "http://"+host+":"+constants.PORT+constants.DOWNLOADV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'fileToDownload':filename}
        reqs = requests.post(reqForm,json=body,cookies=cookies)
        return req

    @abstractmethod
    def upload(self, payload) -> bool:
        #POST requests
        #multipart/form-data
        #qqfile , qquuid , qqfilename , qqpartindex , qqtotalparts , qqtotalfilesize , directoryPath ,
        #credential , id , map , principalMono
        #Response: "success,error"
        raise NotImplemented()
