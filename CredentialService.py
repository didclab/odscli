import requests
import Endpoint
from Endpoint import EndpointType
from Endpoint import EndpointTypeOAUTH
import constants

class CredService:

    def oauth_Url(type:EndpointType)->str:
        oget = "http://"+hostname+":"+constants.PORT+constants.CRED_OAUTH_REGISTERV2
        headers={"Content-Type":"application/json","Authorization": "Bearer "+atok+""}
        greq = requests.get(oget,cookies=cookies,headers=headers)
        greq.text

    def register_Credential(host,type,cred_id,uri,username,secret,atok)->bool:
        credPath = "http://"+host+":"+constants.PORT+constants.CRED_ACCOUNT_REGISTERV2

        credFormated = credPath.format(type=type)
        print(credFormated+"    INFFO")
        cookies = dict(ATOKEN=atok)

        body = {'accountId':cred_id,'uri':uri,'username':username,'secret':secret}

        requests.post(credFormated, cookies=cookies,json=body)

    def get_CredentialODS(type:EndpointType,atok,hostname):

        credPath = "http://"+hostname+":"+constants.PORT+constants.CRED_ACCOUNT_REGISTERV2
        #credPath = "http://"+hostname+":8081"+constants.CRED_ACCOUNT_GETV2

        credFormated = credPath.format(type=type)

        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}

        req = requests.get(credFormated,headers=headers, cookies=cookies)
        return req.json()

    def get_CredentialEnd(type,atok,hostname,user):
        credPath = "http://"+hostname+":"+"8081"+constants.CRED_ACCOUNT_GETV2
        #credPath = "http://"+hostname+":8081"+constants.CRED_ACCOUNT_GETV2

        credFormated = credPath.format(type=type,userId=user)

        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}

        req = requests.get(credFormated,headers=headers, cookies=cookies)
        return req.json()



    def get_OAUTHCredential():
        ## TODO:
        raise NotImplemented()
