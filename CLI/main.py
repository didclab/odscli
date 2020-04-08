#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import getpass
import requests
import json


def argparser_handler(args,token):
    if(args.command=='listDbx'):
        dbxList(args.credential,token)
    elif(args.command=='mkdirDbx'):
        dirDbx(args.credential,args.fileName,token)
    elif (args.command == 'folderlistDbx'):
        folderlistDbx(args.credential,args.fileName,token)
    elif (args.command == 'deleteDbx'):
        deleteDbx(args.credential,args.fileName,token)
    elif (args.command == 'DbxtoGdrive'):
        DbxtoGdrive(args.credential1,args.credential2,args.fileName,token)
        
def parse_args(token):
    parser = argparse.ArgumentParser(description="ODS")
    subparser = parser.add_subparsers(dest='command', metavar='command')
    subparser.required = True
    parser.set_defaults(funct=argparser_handler)
    
    sub_parser_listDbx = subparser.add_parser("listDbx", help="Get DropBox Files.")
    sub_parser_listDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_mkdirDbx = subparser.add_parser("mkdirDbx", help="Make DropBox Folder.")
    sub_parser_mkdirDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    sub_parser_mkdirDbx.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_folderlistDbx = subparser.add_parser("folderlistDbx", help="List DropBox Folder Files.")
    sub_parser_folderlistDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    sub_parser_folderlistDbx.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_deleteDbx = subparser.add_parser("deleteDbx", help="Delete DropBox Files.")
    sub_parser_deleteDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    sub_parser_deleteDbx.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_transferDbxtoGdrive = subparser.add_parser("DbxtoGdrive", help="Transfer Files.")
    sub_parser_transferDbxtoGdrive.add_argument('-src', dest='credential1', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-dest', dest='credential2', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    args = parser.parse_args()
    args.funct(args,token)
    
def dbxList(credential,token):
    if not credential:
        credential=input('DropBox Account:')

    from classes.DropBox import dropBox
    
    instance1=dropBox()
    instance1.credential=credential
    instance1.token=token
    instance1.getDbxList()
    
    
def dirDbx(credential,fileName,token):
    if not credential:
        credential=input('DropBox Account:')
    if not fileName:
        fileName=input('Enter FileName to be Created:')
    from classes.DropBox import dropBox
    
    instance2=dropBox()
    instance2.credential=credential
    instance2.token=token
    instance2.fileName=fileName
    instance2.mkdirDbx()
    
def folderlistDbx(credential,fileName,token):
    if not credential:
        credential=input('DropBox Account:')
    if not fileName:
        fileName=input('Enter Folder Name to be listed:')
    from classes.DropBox import dropBox
    
    instance3=dropBox()
    instance3.credential=credential
    instance3.token=token
    instance3.fileName=fileName
    instance3.folderlistDbx()
    
def deleteDbx(credential,fileName,token):
    if not credential:
        credential=input('DropBox Account:')
    if not fileName:
        fileName=input('Enter File to be deleted:')
    from classes.DropBox import dropBox
    
    instance4=dropBox()
    instance4.credential=credential
    instance4.token=token
    instance4.fileName=fileName
    instance4.deleteDbx()
    
def DbxtoGdrive(credential1,credential2,fileName,token):
    if not credential1:
        credential1=input('DropBox Account:')
    if not credential2:
        credential2=input('GoogleDrive Account:')
    if not fileName:
        fileName=input('Enter File to be transferred:')
    from classes.DropBox import dropBox
    
    instance5=dropBox()
    instance5.credential1=credential1
    instance5.credential2=credential2
    instance5.token=token
    instance5.fileName=fileName
    instance5.transferDbxtoGdrive()
    
def main():
    pass

if __name__ == '__main__':
        user = input("User:") 
        password = getpass.getpass()  
        headers={
            'content-type': 'application/json' 
        }
    
        data={
            "email" : user,
            "password" : password
        }
        
        with requests.Session() as s:       
            url="http://localhost:8080/authenticate"
            req=s.post(url,data=json.dumps(data),headers=headers)
            response=json.loads(req.content)
            token=response['token']
            
        parse_args(token)