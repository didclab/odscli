
import SDK.transfer.source
import SDK.transfer.destination
import SDK.transfer.item

class TransferRequest():
    import SDK.transfer.source
    import SDK.transfer.destination
    import SDK.transfer.item
    source = Source()
    dest = Destination()
    TransfOp:TransferOptions
    priority: int
class TransferOptions():
    compress:bool
    encrypt:bool
    optimizer:string
    overwrite:string
    retry:Integer
    verify:bool

class Transfer():
    def transfer(request: TransferRequest):
        #req = "https://"+host+
        body = {
  "request": {
    "source": {
      "type": TransferRequest.source.type,
      "credId": TransferRequest.source.credentialId,
      "info": TransferRequest.source.info,
      "infoList":TransferRequest.source.infoList
    },
    "destination": {
      "type": TransferRequest.dest.type,
      "credId": TransferRequest.dest.credId,
      "info": TransferRequest.dest.info
    },
    "options": {
      "compress": true,
      "encrypt": true,
      "optimizer": "string",
      "overwrite": true,
      "retry": 0,
      "verify": true
    }
  },
  "principalMono": {
    "name": "string"
  }
}

    def transferStatus(id: str):
        #Todo GetStatus
        raise NotImplemented()

    #def transferFake(request: TransferRequest):
