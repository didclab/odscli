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
        dirDbx(args.credential,args.filename,token)
        
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