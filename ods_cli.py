#CLI IMPORTS
import argparse
import os
import asyncio
import json
import pprint
from datetime import datetime
from SDK.cli_interface import ODSCLI
#SDK IMPORTS
import SDK.token_utils as tokUt
from SDK.credential_service import CredService as CredS
import SDK.endpoint
from SDK.endpoint import Endpoint as endpoint
#import SDK.transfer.transfer
#import SDK.transfer.source
#import SDK.transfer.destination
#import SDK.transfer.item




#Initilization of Interative CLI
async def init(args):
    #Creates Command line interface
    cli = ODSCLI
    await cli.run()
def getOAuthUrlOp(args):
    argsD = vars(args)
    host,user,token = tokUt.readConfig()
    ty = argsD['type']
    try:
        typeE,isOAuth = endpoint.type_handle(ty)
    except:
        print("Type Error")
        return
    req = CredS.oauth_Url(host,typeE,token)
    #print(req)

def transferOp(args):
    argsD = vars(args)
    source = argsD["S"]
    dest = argsD["D"]
    Stype = source[0:source.find(':')]
    ScredId = source[source.find(':')+1:source.find('@')]
    Sinfo = "'id':'','path':'{}','size':''".format(source[source.rindex('@')+1:])
    Sinfo = "{"+Sinfo+"}"
    Dtype = dest[0:dest.find(':')]
    DcredId = dest[dest.find(':')+1:dest.find('@')]
    Dinfo = "'id':'','path':'{}','size':''".format(dest[dest.rindex('@')+1:])

    host, user, token = tokUt.readConfig()
    body = {
      "request": {
        "source": {
          "type": Stype,
          "credId": ScredId,
          "info": Sinfo,
          "infoList":Sinfo
        },
        "destination": {
          "type": Dtype,
          "credId": DcredId,
          "info": Dinfo
        },
        "options": {
          "compress": True,
          "encrypt": True,
          "optimizer": "string",
          "overwrite": True,
          "retry": 0,
          "verify": True
        }
      },
      "principalMono": {
        "name": "string"
      }
    }
    #jsOb = json.loads(body)
    pp = pprint.PrettyPrinter(indent = 3)
    pp.pprint(body)
    print("\n\nResponse: String ID")
    #print(body)

def mkdirOp(args):
    argsD = vars(args)
    host, user, token = tokUt.readConfig()
    r,p = argsD['type:remote@path'].split('@')
    t,r = r.split(':')
    p,d = p[0:p.rindex('/')],p[p.rindex('/')+1:]
    #print(host+"|"+p+"|"+d+"|"+r+"|")
    ret = endpoint.mkdir(host, '/', p, r, t, token,d)
    print(ret)

def loginUser(args):
    argD = vars(args)
    work,tok = tokUt.login(host=argD['hostname'],user=argD['user'],password=argD['passw'])
    if work:
        return True
    else:
        return False

def addRemoteEnd(args):
    argsD = vars(args)
    try:
        typeE,isOAuth = endpoint.type_handle(argsD["type"])
    except:
        print("Type Error")
        return
    host,user,token = tokUt.readConfig()
    if isOAuth:
        CredS.oauth_Url(host,typeE,token)
    else:
        CredS.register_Credential(host,typeE,argsD['host'],argsD['path'],argsD['user'],argsD['passw'],token)

def listOp(args):
    #print(args)
    argsD = vars(args)
    host,user,token = tokUt.readConfig()
    r,p = argsD['type:remote@path'].split('@')
    t,r = r.split(':')
    jsonstr = endpoint.list(r,p,p,host,t,token)
    jsonOb = json.loads(jsonstr)
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
    argsD = vars(args)
    host,user,token = tokUt.readConfig()
    ty = argsD['type']
    req = CredS.get_CredentialODS(ty,token,host)
    print(req)

def listRemoteEndOp(args):
    argsD = vars(args)
    host,user,token = tokUt.readConfig()
    ty = argsD['type']
    req = CredS.get_CredentialEnd(ty,token,host,user)
    print(req)


def parseArgFunc():
    #defining top level parser
    parser = argparse.ArgumentParser(description='OneDataShare Command Line Tool')
    #defining sub command parser
    subparser = parser.add_subparsers(title="Commands",description="Commands to run",help="more help for commands")
    #Adding parsers onto subparser and giving them arguments and functions
    list = subparser.add_parser("list")
    list.set_defaults(func=listOp)
    #list.add_argument(":")
    list.add_argument("type:remote@path")
    list.add_argument("-p",dest='print')
    #list.add_argument("-path",default="/",dest="path")

    mkdir = subparser.add_parser("mkdir")
    mkdir.set_defaults(func=mkdirOp)
    #mkdir.add_argument(':')
    mkdir.add_argument('type:remote@path')

    addRemote = subparser.add_parser("addRemote")
    addRemote.set_defaults(func=addRemoteEnd)
    addRemote.add_argument("-user",default="",dest="user")
    addRemote.add_argument("-pass",default="",dest="passw")
    addRemote.add_argument("-host",default="",dest="host")
    addRemote.add_argument("-type",required=True,dest="type")
    addRemote.add_argument("-path",default="/",dest="path")     #DEFAULT PATH == /

    listRemotes = subparser.add_parser("listRemotes")
    listRemotes.set_defaults(func=listRemoteOp)
    #listRemotes.add_argument("-host")
    listRemotes.add_argument("-type",required=True,dest="type")

    listRemotesEnd = subparser.add_parser("listRemotesEndpoint")
    listRemotesEnd.set_defaults(func=listRemoteEndOp)
    listRemotesEnd.add_argument("-type",required=True,dest="type")

    login = subparser.add_parser("login")
    login.set_defaults(func=loginUser)
    login.add_argument("-user",required=True,dest="user")
    login.add_argument("-pass",required=True,dest="passw")
    login.add_argument("-host",dest="hostname",default="onedatashare.org")      #DEFAULT HOST == onedatashare.org

    transfer = subparser.add_parser("transfer")
    transfer.set_defaults(func=transferOp)
    transfer.add_argument("-S")
    transfer.add_argument("-D")
    #transfer.add_argument("-Stype")
    #transfer.add_argument("-ScredId")
    #transfer.add_argument("-Sinfo",default="{'id':'','path':'','size':''}")
    #transfer.add_argument("-SinfoList",default="{'id':'','path':'','size':''}")
    #transfer.add_argument("-Dtype")
    #transfer.add_argument("-DcredId")
    #transfer.add_argument("-Dinfo",default="{'id':'','path':'','size':''}")
    #transfer.add_argument()

    getOAuthUrl = subparser.add_parser("getOAuthUrl")
    getOAuthUrl.set_defaults(func=getOAuthUrlOp)
    getOAuthUrl.add_argument("-type")
    #DEBUG
    #print(vars(args))
    return parser

if __name__ == '__main__':
    parser = parseArgFunc()
    args = parser.parse_args()
    #args = parseArgFunc()

    #checking for super user permissions (ONLY FOR INTERACTIVE MODE)
    if not vars(args):
        if not os.geteuid() == 0:
            raise PermissionError('This Client must be run with super user permissions')
        #creating event loop for command prompt and start init with the arguments passed in
        prompt = asyncio.get_event_loop()
        prompt.run_until_complete(init(args))
    else:
        #DEBUG
        #rint("Called Arg Function")
        args.func(args)
