from Endpoint import EndpointType
from Item import Iteminfo

type:EndpointType
credentialId:string
info:Iteminfo
infoList:Iteminfo

def Source(type: EndpointType, credentialId: string, info: Iteminfo):
    this.type = type
    this.credentialId = credentialId
    this.info = info
