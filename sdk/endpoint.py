import requests
import json
import sdk.token_utils as tokenUtils
from abc import ABC, abstractmethod
from enum import Enum
import sdk.constants as constants

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
    #NEEDS TO BE IMPLEMENTED FOR sdk
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

    def list(credId,host,type,atok, path="", id="") -> str:
        req = constants.ODS_PROTOCOL+host+constants.LISTV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':credId,'path':path,'identifier':id}
        print(body)
        res = requests.get(reqForm,params=body,cookies=cookies)# Needs to be handled better for errors
        return res.text

    def mkdir(credId, host, type, atok, folderToCreate, path="", id="") -> str:
        req = constants.ODS_PROTOCOL+host+constants.MKDIRV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':credId,'path':path,'id':id,'folderToCreate':folderToCreate}
        res = requests.post(reqForm,json=body,cookies=cookies)# Needs to be handled better for errors
        return res

    def remove(credId, host, type, atok, toDelete, path="", id="") -> str:
        req = constants.ODS_PROTOCOL+host+constants.REMOVEV2
        reqForm = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body={'credId':credId,'path':path,'id':id,'toDelete':toDelete}
        print(body)
        res = requests.post(reqForm,json=body,cookies=cookies)# Needs to be handled better for errors
        return res
