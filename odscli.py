import argparse
import os
import asyncio
import tokenUtils as tokUt
from CredentialService import CredService as CredS
import Endpoint
from Endpoint import endpoint
import json

from cli_interface import ODSCLI


#Initilization of Interative CLI
async def init(args):
    #Creates Command line interface
    cli = ODSCLI
    await cli.run()

def mkdirOp(args):
    argsD = vars(args)
    host, user, token = tokUt.readConfig()
    r,p = argsD['remote@path'].split('@')
    p,d = p[0:p.rindex('/')+1],p[p.rindex('/')+1:]
    print(host+"|"+p+"|"+d+"|"+r+"|")
    ret = endpoint.mkdir(host, '/', p, r, argsD[':'][1:], token,d)

def loginUser(args):
    argD = vars(args)
    work,tok = tokUt.login(host=argD['hostname'],user=argD['user'],password=argD['passw'])
    if work:
        return True
    else:
        return False

def addRemoteEnd(args):
    argsD = vars(args)
    typeE,isOAuth = endpoint.type_handle(argsD["type"])
    host,user,token = tokUt.readConfig()
    if isOAuth:
        CredS.oauth_Url
    else:
        CredS.register_Credential(host,typeE,argsD['host'],argsD['path'],argsD['user'],argsD['passw'],token)

def listOp(args):
    argsD = vars(args)
    host,user,token = tokUt.readConfig()
    r,p = argsD['remote@path'].split('@')
    jsonstr = endpoint.list(r,p,p,host,argsD[':'][1:],token)
    jsonOb = json.loads(jsonstr)
    diction = jsonOb
    print("-[DIR]"+diction.get('name')+"\n")
    diction = diction.get('files')
    for names in diction:
        print("--"+names.get('name'),end = " : ")
        if names.get("dir") == True:
            print("[DIR]\n")
        else:
            print("\n")



def parseArgFunc():
    #defining top level parser
    parser = argparse.ArgumentParser(description='OneDataShare Command Line Tool')
    #defining sub command parser
    subparser = parser.add_subparsers(title="Commands",description="Commands to run",help="more help for commands")
    #Adding parsers onto subparser and giving them arguments and functions
    list = subparser.add_parser("list")
    list.set_defaults(func=listOp)
    list.add_argument(":")
    list.add_argument("remote@path")
    #list.add_argument("-path",default="/",dest="path")

    mkdir = subparser.add_parser("mkdir")
    mkdir.set_defaults(func=mkdirOp)
    mkdir.add_argument(':')
    mkdir.add_argument('remote@path')

    addRemote = subparser.add_parser("addRemote")
    addRemote.set_defaults(func=addRemoteEnd)
    addRemote.add_argument("-user",default="",dest="user")
    addRemote.add_argument("-pass",default="",dest="passw")
    addRemote.add_argument("-host",required=True,dest="host")
    addRemote.add_argument("-type",required=True,dest="type")
    addRemote.add_argument("-path",default="/",dest="path")     #DEFAULT PATH == /

    listRemotes = subparser.add_parser("listRemotes")
    listRemotes.add_argument("-host")
    listRemotes.add_argument("-type")

    login = subparser.add_parser("login")
    login.set_defaults(func=loginUser)
    login.add_argument("-user",required=True,dest="user")
    login.add_argument("-pass",required=True,dest="passw")
    login.add_argument("-host",dest="hostname",default="onedatashare.org")      #DEFAULT HOST == onedatashare.org

    args = parser.parse_args()
    #DEBUG
    print(vars(args))
    return args

if __name__ == '__main__':

    args = parseArgFunc()

    #checking for super user permissions (ONLY FOR INTERACTIVE MODE)
    if not vars(args):
        if not os.geteuid() == 0:
            raise PermissionError('This Client must be run with super user permissions')
        #creating event loop for command prompt and start init with the arguments passed in
        prompt = asyncio.get_event_loop()
        prompt.run_until_complete(init(args))
    else:
        #DEBUG
        print("Called Arg Function")
        args.func(args)
