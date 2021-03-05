import requests
import SDK.endpoint
from SDK.endpoint import EndpointType
from SDK.endpoint import EndpointTypeOAUTH
import SDK.constants as constants

class CredService:

    def oauth_Url(host,type,atok)->str:
        req = "http://"+host+":"+constants.PORT+constants.CRED_OAUTH_REGISTERV2
        body = {}
        query= {"type":type}
        headers={"accept":"application/json","Authorization": "Bearer "+atok+""}
        greq = requests.get(req,headers=headers,json=body,params=query,allow_redirects=False)
        print(greq.headers["Location"])

    def register_Credential(host,type,cred_id,uri,username,secret,atok)->bool:
        req = "http://"+host+":"+constants.PORT+constants.CRED_ACCOUNT_REGISTERV2
        reqFormated = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        body = {'accountId':cred_id,'uri':uri,'username':username,'secret':secret}
        requests.post(reqFormated, cookies=cookies,json=body)

    def get_CredentialODS(type:EndpointType,atok,hostname):
        req = "http://"+hostname+":"+constants.PORT+constants.CRED_ACCOUNT_REGISTERV2
        #credPath = "http://"+hostname+":8081"+constants.CRED_ACCOUNT_GETV2
        reqFormated = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}
        req = requests.get(reqFormated,headers=headers, cookies=cookies)
        return req.json()

    def get_CredentialEnd(type,atok,hostname,user):
        req = "http://"+hostname+":"+"8081"+constants.CRED_ACCOUNT_GETV2
        reqFormated = req.format(type=type,userId=user)
        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}
        req = requests.get(reqFormated,headers=headers, cookies=cookies)
        return req.json()



    def get_OAUTHCredential():
        ## TODO:
        raise NotImplemented()
