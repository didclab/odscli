import requests
import sdk.endpoint
from sdk.endpoint import EndpointType
from sdk.endpoint import EndpointTypeOAUTH
import sdk.constants as constants


class CredService:        

    def oauth_Url(host,type,atok)->str:
        req = constants.ODS_PROTOCOL+host+constants.CRED_OAUTH_REGISTERV2
        body = {}
        query= {"type":type}
        headers={"accept":"application/json","Authorization": "Bearer "+atok+""}
        greq = requests.get(req,headers=headers,json=body,params=query,allow_redirects=False)# Needs to be handled better for errors
        print(greq.headers["Location"])

    def register_Credential(host,type,cred_id,uri,username,secret,atok)->bool:
        req = constants.ODS_PROTOCOL+host+constants.CRED_ACCOUNT_REGISTERV2
        reqFormated = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        print(secret)
        body = {'accountId':cred_id,'uri':uri,'username':username,'secret':secret}
        requests.post(reqFormated, cookies=cookies,json=body)# Needs to be handled better for errors

    def get_CredentialODS(type:EndpointType,atok,hostname):
        req = constants.ODS_PROTOCOL+hostname+constants.CRED_ACCOUNT_REGISTERV2
        reqFormated = req.format(type=type)
        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}
        req = requests.get(reqFormated,headers=headers, cookies=cookies)# Needs to be handled better for errors
        return req.json()
        
    def delete_CredentialODS(type:EndpointType,credID,atok,hostname):
        req = constants.ODS_PROTOCOL+hostname+constants.CRED_ACCOUNT_DELETE
        reqFormated = req.format(type=type,credID=credID)
        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}
        req = requests.delete(reqFormated,headers=headers, cookies=cookies)# Needs to be handled better for errors
        return req

    def get_CredentialEnd(type,atok,hostname,user):
        req = constants.ODS_PROTOCOL+hostname+":"+"8081"+constants.CRED_ACCOUNT_GETV2
        reqFormated = req.format(type=type,userId=user)
        cookies = dict(ATOKEN=atok)
        headers = {"Authorization": "Bearer "+atok+""}
        req = requests.get(reqFormated,headers=headers, cookies=cookies)# Needs to be handled better for errors
        return req

    def get_OAUTHCredential():
        ## TODO:
        raise NotImplemented()
