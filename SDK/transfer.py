import json
import requests
import SDK.constants as constants


class Iteminfo():
    def __init__(self,id:str = "", path:str = "",size:int = -1):
        self.id = id
        self.path = path
        self.size = size

class Source():
    def __init__(self,type: str = "", credentialId: str = "",parentInfo:Iteminfo = Iteminfo("","",-1), info: Iteminfo = Iteminfo("","",-1)):
        self.type = type
        self.credentialId = credentialId
        self.info = info
        self.parentInfo = parentInfo

class Destination():
    def __init__(self,type: str = "", credentialId: str = "", info: Iteminfo = Iteminfo()):
        self.type = type
        self.credentialId = credentialId
        self.info = info

class TransferOptions():
    def __init__(self,concurrencyThreadCount:int = 1,pipeSize:int = 1, chunkSize:int = 640000, parallelThreadCount:int = 1,compress:bool = False,encrypt:bool = False,optimize:str = "",overwrite:str = "",retry:int = 1,verify:bool = False):
        self.concurrencyThreadCount = concurrencyThreadCount
        self.pipeSize = pipeSize
        self.chunkSize = chunkSize
        self.parallelThreadCount = parallelThreadCount
        self.compress = compress
        self.encrypt = encrypt
        self.optimize = optimize
        self.overwrite = overwrite
        self.retry = retry
        self.verify = verify

class TransferRequest():
    def __init__(self,source:Source = Source(),dest:Destination = Destination(),TransfOp:TransferOptions = TransferOptions(),priority:int = 0):
        self.source = source
        self.dest = dest
        self.TransfOp = TransfOp
        self.priority = priority

class Transfer():
    def transfer(host,token,request:TransferRequest):
        #Need to add parallelism
        #need to add parent ID and parent PATH
        #need to add info ID and info PATH
        #need to add more options (compress encrypt optimizer)**support these first
        body={"source":{"type":request.source.type,"credId":request.source.credentialId,"parentInfo":{"id":request.source.parentInfo.id,"path":request.source.parentInfo.path,"size":request.source.parentInfo.size},"infoList":[{"id":request.source.info.id,"path":request.source.info.path}]},"destination":{"type":request.dest.type,"credId":request.dest.credentialId,"parentInfo":{"id":request.dest.info.id,"path":request.dest.info.path,"size":request.dest.info.size}},"options":{"concurrencyThreadCount":request.TransfOp.concurrencyThreadCount,"pipeSize":request.TransfOp.pipeSize,"chunkSize":request.TransfOp.chunkSize,"parallelThreadCount":request.TransfOp.parallelThreadCount}}
        jsOb = json.dumps(body)
        hoststring = "http://"+host+":"+constants.PORT+constants.TRANSFER
        cookies = dict(ATOKEN=token)
        headers={"Content-Type":"application/json","Authorization": "Bearer "+token+""}
        r = requests.post(hoststring,headers=headers,cookies=cookies,data=jsOb)# Needs to be handled better for errors
        return r


    def transferStatus(id: str):
        #Todo GetStatus
        raise NotImplemented()

    #def transferFake(request: TransferRequest):
