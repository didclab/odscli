import requests
import json
import SDK.token_utils as tokenUtils
from abc import ABC, abstractmethod
from enum import Enum
import SDK.constants as constants

class EndpointType(Enum):
    VFS = "vfs"
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
        req = requests.get(reqForm,params=body,cookies=cookies)# Needs to be handled better for errors
        if req.status_code==200:
            print(req.text())
            return req.text
        else:
            print("Error Handling list")
            return False,""

    def mkdir(remoteHost, path, identifier, host, type, atok,dirToAdd) -> str:
        req = "http://"+host+":"+constants.PORT+constants.MKDIRV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'folderToCreate':dirToAdd}
        reqs = requests.post(reqForm,json=body,cookies=cookies)# Needs to be handled better for errors
        if reqs.status_code==200:
            print(reqs.text())
            return reqs.text
        else:
            print("Error Handling mkdir")
            return False,""

    def remove(remoteHost, path, identifier, host, type, atok,filename) -> str:
        req = "http://"+host+":"+constants.PORT+constants.REMOVEV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':remoteHost,'path':path,'id':identifier,'toDelete':filename}
        reqs = requests.post(reqForm,json=body,cookies=cookies)# Needs to be handled better for errors
        if reqs.status_code==200:
            print(reqs.text())
            return reqs.text
        else:
            print("Error Handling remove")
            return False,""
        return req
