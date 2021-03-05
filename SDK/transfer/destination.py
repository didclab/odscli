from SDK.transfer.item import Iteminfo
class Destination():
    type:str
    credentialId:str
    info:Iteminfo

def Destination(type: str, credentialId: str, info: Iteminfo):
    this.type = type
    this.credentialId = credentialId
    this.info = info
