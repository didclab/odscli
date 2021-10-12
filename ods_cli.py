#CLI IMPORTS
import argparse
import os
import json
import pprint
import requests
from datetime import datetime
#SDK IMPORTS
import SDK.token_utils as tokUt
from SDK.credential_service import CredService as CredS
import SDK.endpoint
from SDK.endpoint import Endpoint as endpoint
from SDK.transfer import TransferRequest
from SDK.transfer import TransferOptions
from SDK.transfer import Source
from SDK.transfer import Destination
from SDK.transfer import Iteminfo
from SDK.transfer import Transfer as Transfer

## TODO: Add exceptions or text so users cannot use other functions when not logged in
def loadConfig():
    try:
        host,user,token = tokUt.readConfig()
    except KeyError:                            #THIS SHOULD PROBABLY MOVE TO TOKEN UTILS
        print("User not logged in, No Config")
        exit()
    if host and user and token == 'None':
        print("User not logged in, Cleared Config")
        exit()
    return host,user,token


def getOAuthUrlOp(args):
    host,user,token = loadConfig()
    ty = args['type']
    try:
        typeE,isOAuth = endpoint.type_handle(ty)
    except:
        print("Type Error")
        return
    req = CredS.oauth_Url(host,typeE,token)
    #print(req)

#Transfer Operation
#Inputs (Parsed Args Namespace)
def transferOp(argsD):
    host, user, token = loadConfig()
    source = Source(argsD["Source_type"], argsD["Source_credID"], Iteminfo(argsD["Source_Path"], argsD["Source_Path"], 0), Iteminfo(argsD["Source_File"], argsD["Source_File"], 0))
    source.type = argsD["Source_type"]
    dest = Destination(argsD["Dest_type"],argsD["Dest_credID"],Iteminfo(argsD["Dest_Path"],argsD["Dest_Path"],0))
    transfOp = TransferOptions(argsD["concurrency"],argsD["piping"],argsD["chunkSize"])
    transfReq = TransferRequest(source,dest,transfOp,1)
    r = Transfer.transfer(host,token,transfReq)
    print("status code: "+str(r.status_code))
    print(r.text)


def jobQueryOp(argsD):
    hostname, jobName, stepName, instanceID, isDirectory = argsD['hostname'],argsD['jobName'],argsD['stepName'],argsD['instanceID'],argsD['isDirectory']
    body = {"jobName":jobName,"instanceId":instanceID,"stepName":stepName,"isDirectory":isDirectory}
    hoststring = "http://"+hostname+":8092/api/v1/query/job_status"
    print("\n")
    print(hoststring)
    r = requests.post(hoststring,body)
    print(r.status_code)
    print("\n\n")
    print(r)


def mkdirOp(args):
    host, user, token = loadConfig()
    #r,p = args['type:remote@path'].split('@')
    #t,r = r.split(':')
    #p,d = p[0:p.rindex('/')],p[p.rindex('/')+1:]
    r = args["credId"]
    p = args["path"]
    t = args["type"]
    d = args["newDir"]
    ret = endpoint.mkdir(host, '/', p, r, t, token,d)
    print(ret)

def loginUser(args):
    work,tok = tokUt.login(host=args['hostname'],user=args['user'],password=args['passw'])
    if work:
        print("\nSuccessfully Logged In!\n")
    else:
        print("\nProblem Logging In\n")
def logoutUser(args):
    tokUt.logout()
    print("\nLogged Out\n")

def addRemoteEnd(args):
    try:
        typeE,isOAuth = endpoint.type_handle(args["type"])
    except:
        print("Type Error")
        return
    host,user,token = tokUt.readConfig()
    if isOAuth:
        CredS.oauth_Url(host,typeE,token)
    else:
        # First, check to make sure both are not none.
        if args['keyfile'] == "" and args['passw'] == "":
            print("Password Error: No password given")

        # If the code has gotten here, that means that either the keyfile or the password is valid. 
        # However, it is also possible that BOTH are valid, which is also an error. 

        elif args['keyfile'] != "" and args['passw'] != "":
            print("Password Error: Both password types given, please only provide one")

        # Now, we can conclude that only one of the two password types were given.

        else:
            if args['keyfile'] != "":
                print("Used the keyfile")
                keyfile = args['keyfile']
                if keyfile.endswith('.pem'):
                    with open(keyfile, "r") as f:
                        keyfile = f.read()
                    CredS.register_Credential(host,typeE,args['accountID'],args['host'],args['user'],keyfile,token)
                else:
                    print("Password Error: The PEM key you provided was malformed, it must end with a .pem file extension.")
            else:
                print("Used the password")
                CredS.register_Credential(host,typeE,args['accountID'],args['host'],args['user'],args['passw'],token)


def deleteRemoteEnd(args):
    try:
        typeE,isOAuth = endpoint.type_handle(args["type"])
    except:
        print("Type Error")
        return
    host,user,token = loadConfig()
    if isOAuth:
        print("deleting oauth credentials is not supported yet")
    else:
        req = CredS.delete_CredentialODS(typeE,args["credID"],token,host)# Needs to be handled better for errors
        if req.status_code != 200:
            print("error with deleting")
        elif req.status_code == 200:
            print("Credential Deleted")


def listOp(args):
    host,user,token = loadConfig()
    #r,p = args['type:remote@path'].split('@')
    #t,r = r.split(':')
    t = args["type"]
    r = args["credId"]
    p = args["path"]
    jsonstr = endpoint.list(r,p,p,host,t,token)# Needs to be handled better for errors
    jsonOb = json.loads(jsonstr)# Needs to be handled better for errors
    diction = jsonOb
    pad = len(str(diction.get("size")))
    padN = len(str(diction.get("name")))
    temp = diction.get("files")
    for names in temp:
        if len(str(names.get('size'))) > pad:
            pad = len(str(names.get('size')))
        if len(str(names.get('name'))) > padN:
            padN = len(str(names.get('name')))
    print("Permissions\tSize\tTime\tDir\tName\tid\n")
    formating = "{}\t{:>"+str(pad)+"}\t{}\t{}\t.({})\t{}\n"
    print(formating.format(diction.get('permissions'),diction.get('size'),datetime.fromtimestamp(diction.get('time')),diction.get('dir'),diction.get('name'),diction.get('id')))
    diction = diction.get('files')
    if argsD['print'] == 'json':
        print(json.dumps(jsonOb))
    else:
        for names in diction:
            formating = "{}\t{:>"+str(pad)+"}\t{}\t{}\t{:>"+str(padN)+"}\t{}\n"
            print(formating.format(names.get('permissions'),names.get('size'),datetime.fromtimestamp(names.get('time')),names.get('dir'),names.get('name'),names.get('id')))

def listRemoteOp(args):
    host,user,token = loadConfig()
    ty = args['type']
    req = CredS.get_CredentialODS(ty,token,host) # Needs to be handled better for errors
    print("Remotes:\n")
    for cred in req["list"]:
        print("\t"+cred)

#Not needed, Used to list endpoints directly from credential service
def listRemoteEndOp(args):
    host,user,token = loadConfig()
    ty = args['type']
    req = CredS.get_CredentialEnd(ty,token,host,user) # Needs to be handled better for errors
    print(req)

#TODO add better help descriptions
def parseArgFunc():
    #defining top level parser
    parser = argparse.ArgumentParser(description='OneDataShare Command Line Tool')
    #defining sub command parser
    subparser = parser.add_subparsers(title="Commands",description="Commands to manage OneDataShare",help="All commands have a help flag")
    #Adding parsers onto subparser and giving them arguments and functions
    login = subparser.add_parser("login",help="Login to OneDataShare backend, saves information to local file")
    login.set_defaults(func=loginUser)
    login.add_argument("-user",required=True,dest="user",help="Username for OneDataShare application (Website)")
    login.add_argument("-pass",required=True,dest="passw",help="Password for OneDataShare application (Website)")
    login.add_argument("-host",dest="hostname",default="onedatashare.org",help="Hostname for OneDataShare application (Default: onedatashare.org)")      #DEFAULT HOST == onedatashare.org

    logout = subparser.add_parser("logout",help="Logout of OneDataShare backend, clears information file")
    logout.set_defaults(func=logoutUser)

    addRemote = subparser.add_parser("addRemote",help="Save a Credential to OneDataShare backend")
    addRemote.set_defaults(func=addRemoteEnd)
    addRemote.add_argument("-user",default="",dest="user",help="Username for remote endpoint")
    addRemote.add_argument("-pass",default="",dest="passw",help="Password for remote endpoint")
    addRemote.add_argument("-host",default="",dest="host",help="Hostname for remote endpoint")
    addRemote.add_argument("-type",required=True,dest="type",help="Type of remote endpoint")
    addRemote.add_argument("-credentialId","-ci",dest="accountID",help="Custom name for new remote endpoint credential")     #DEFAULT PATH == /
    addRemote.add_argument("-keyfile",default="",dest="keyfile",help="A PEM key used as an alternative means of logging in")
    #add new argument for key file "-keyFile or something"

    listRemotes = subparser.add_parser("listRemotes",help="List the saved remotes of a certain type")
    listRemotes.set_defaults(func=listRemoteOp)
    listRemotes.add_argument("-type",required=True,dest="type",help="Type of remote endpoint")

    deleteRemote = subparser.add_parser("deleteRemote",help="Delete a saved remote")
    deleteRemote.set_defaults(func=deleteRemoteEnd)
    deleteRemote.add_argument("-type",required=True,dest="type",help="Type of remote endpoint")
    deleteRemote.add_argument("-credentialId","-ci",required=True,dest="credID",help="Credential name for remote endpoint")

    list = subparser.add_parser("list",help="List the contents of a remote")
    list.set_defaults(func=listOp)
    list.add_argument("-type",required=True,dest="type",help="Type of remote endpoint")
    list.add_argument("-credentialId","-ci",required=True,dest="credId",help="Credential name for remote endpoint")
    list.add_argument("-path",required=False,dest="path",default="",help="Path for remote endpoint (default: / )")
    list.add_argument("-p",dest='print',help="(OPTIONAL)Print option, Default: Pretty Print, Optional{-p json}: Prints JSON output")

    mkdir = subparser.add_parser("mkdir",help="Make a Directory on a remote")
    mkdir.set_defaults(func=mkdirOp)
    #mkdir.add_argument('type:remote@path')#Old way of parsing similar to normal linux tools
    mkdir.add_argument("-type",required=True,dest="type",help="Type of remote endpoint")
    mkdir.add_argument("-credentialId","-ci",required=True,dest="credId",help="Credential name for remote endpoint")
    mkdir.add_argument("-path",required=False,dest="path",help="Path to where the new directory will go(default: / )")
    mkdir.add_argument("-newDir",required=True,dest="newDir",help="New directory to create")

    transfer = subparser.add_parser("transfer",help="Transfer between two remotes")
    transfer.set_defaults(func=transferOp)
    transfer.add_argument("-Source-type","-st",required=True,help="Source credential type")
    transfer.add_argument("-Source-credID","-sc",help="Source credential name")
    transfer.add_argument("-Source-File","-sf",help="Source file name")
    transfer.add_argument("-Source-Path","-sp",help="Path to source file")
    transfer.add_argument("-Dest-type","-dt",help="Destinaltion credential type")
    transfer.add_argument("-Dest-credID","-dc",help="Destination credential name")
    transfer.add_argument("-Dest-Path","-dp",help="Path to destination directory")
    transfer.add_argument("-concurrency","-cc",default=1,help="Concurreny Level (default: 1 )")
    transfer.add_argument("-piping","-ps",default=1,help="Pipe Size (default: 1 )")
    transfer.add_argument("-chunkSize","-cs",default=640000,help="Chunk Size (default: 640000 )")

    jobQuery = subparser.add_parser("jobQuery",help="Query about an ongoing/previous transfer")
    jobQuery.set_defaults(func=jobQueryOp)
    jobQuery.add_argument("-hostname")
    jobQuery.add_argument("-jobName")
    jobQuery.add_argument("-instanceID")
    jobQuery.add_argument("-stepName")
    jobQuery.add_argument("-isDirectory")

    getOAuthUrl = subparser.add_parser("getOAuthUrl",help="Get a URL to Authorize the use of OAUTH remotes")
    getOAuthUrl.set_defaults(func=getOAuthUrlOp)
    getOAuthUrl.add_argument("-type")
    #DEBUG
    #print(vars(args))
    return parser

if __name__ == '__main__':
    parser = parseArgFunc()
    args = parser.parse_args()
    argsD = vars(args)
    if (argsD=={}):
        print("\nNo arguments provided, please try -h for help\n")
        exit()
    args.func(argsD)
