from Endpoint import EndpointType
from Item import Iteminfo

type:EndpointType
credentialId:String
info:Iteminfo

def Destination(type: EndpointType, credentialId: string, info: Iteminf):
    this.type = type
    this.credentialId = credentialId
    this.info = info
