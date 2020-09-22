
class TransferRequest():
    source: Source
    dest:Destination
    TransfOp:transferOptions
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
        body = {
  "request": {
    "source": {
      "type": TransferRequest.source.type,
      "credId": TransferRequest.source.credentialId,
      "info": TransferRequest.source.info,
      "infoList":TransferRequest.source.infoList
    },
    "destination": {
      "type": TransferRequest,
      "credId": "string",
      "info": {
        "id": "string",
        "path": "string",
        "size": 0
      }
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
