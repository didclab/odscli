
from SDK.transfer.item import Iteminfo
class Source():
    type:str
    credentialId:str
    info:Iteminfo
    infoList:Iteminfo

def Source(type: str, credentialId: str, info: Iteminfo):
    this.type = type
    this.credentialId = credentialId
    this.info = info
