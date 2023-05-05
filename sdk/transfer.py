import json
import requests
import sdk.constants as constants


class Iteminfo():
    def __init__(self, id:str = "", path:str = "", size:int = -1, chunk_size:int=10000000):
        self.id = id
        self.path = path
        self.size = size
        self.chunkSize = chunk_size

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class Source():
    def __init__(self,infoList=[], type: str="", credentialId: str = "",parentInfo:Iteminfo = Iteminfo("","",-1)):
        self.type = type
        self.credId = credentialId
        self.infoList = infoList
        self.parentInfo = parentInfo
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Destination():
    def __init__(self,type: str = "", credentialId: str = "", parentInto: Iteminfo = Iteminfo()):
        self.type = type
        self.credId = credentialId
        self.parentInfo = parentInto

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class TransferOptions():
    def __init__(self,concurrencyThreadCount:int = 1,pipeSize:int = 1, chunkSize:int = 640000, parallelThreadCount:int = 1,compress:bool = False,encrypt:bool = False,optimizer:str = "",overwrite:str = "",retry:int = 1,verify:bool = False):
        self.concurrencyThreadCount = concurrencyThreadCount
        self.pipeSize = pipeSize
        self.chunkSize = chunkSize
        self.parallelThreadCount = parallelThreadCount
        self.compress = compress
        self.encrypt = encrypt
        self.optimizer = optimizer
        self.overwrite = overwrite
        self.retry = retry
        self.verify = verify

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class TransferRequest():
    def __init__(self,source:Source = Source(),dest:Destination = Destination(),TransfOp:TransferOptions = TransferOptions()):
        self.source = source
        self.destination = dest
        self.options = TransfOp
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

class Transfer():
    def transfer(host,token,request:TransferRequest):
        #Need to add parallelism
        #need to add parent ID and parent PATH
        #need to add info ID and info PATH
        #need to add more options (compress encrypt optimizer)**support these first
        # body={"source":{"type":request.source.type,"credId":request.source.credentialId,"parentInfo":{"id":request.source.parentInfo.id,"path":request.source.parentInfo.path,"size":request.source.parentInfo.size},"infoList":[{"id":request.source.info.id,"path":request.source.info.path}]},"destination":{"type":request.destination.type,"credId":request.destination.credentialId,"parentInfo":{"id":request.destination.info.id,"path":request.destination.info.path,"size":request.destination.info.size}},"options":{"concurrencyThreadCount":request.options.concurrencyThreadCount,"pipeSize":request.options.pipeSize,"chunkSize":request.options.chunkSize,"parallelThreadCount":request.options.parallelThreadCount}}
        # jsOb = json.dumps(body)
        hoststring = constants.ODS_PROTOCOL+host+constants.TRANSFER
        # print(hoststring)
        cookies = dict(ATOKEN=token)
        headers={"Content-Type":"application/json","Authorization": "Bearer "+token+""}
        print(request.toJSON())
        r = requests.post(hoststring,headers=headers,cookies=cookies,data=request.toJSON())# Needs to be handled better for errors
        return r

    def transferStatus(id: str):
        #Todo GetStatus
        raise NotImplemented()

    #def transferFake(request: TransferRequest):
