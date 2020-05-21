#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from endpoint.Dropbox import dropbox
from endpoint.Gdrive import gdrive
from endpoint.Box import box
from endpoint.Endpoint import endpoint


def argparser_handler(args):
    if(args.command=='ls'):
        if(args.fileName==None):
            list(args.credential)
        else:
            folderlist(args.credential,args.fileName)
    elif(args.command=='mkdir'):
        mkdir(args.credential,args.fileName)
    elif (args.command == 'rm'):
        delete(args.credential,args.fileName)
    elif (args.command == 'download'):
        download(args.credential,args.fileName)
    elif (args.command == 'transfer'):
        transfer(args.credential1,args.credential2,args.fileName)

        
def parse_args():
    parser = argparse.ArgumentParser(description="ODS")
    
 
    subparser = parser.add_subparsers(dest='command', metavar='command')
    subparser.required = True
    parser.set_defaults(funct=argparser_handler)
    
    sub_parser_list = subparser.add_parser("ls", help="List Files and Folders.")
    sub_parser_list.add_argument("credential")
    sub_parser_list.add_argument('-f', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    #sub_parser_listDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_mkdir = subparser.add_parser("mkdir", help="Make Folder.")
    sub_parser_mkdir.add_argument("fileName")
    sub_parser_mkdir.add_argument("credential")
    
    #parser.add_argument('string', help='Input String', nargs='+', action=dirDbx)
    #sub_parser_mkdir.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    #sub_parser_mkdirDbx.add_argument('file', metavar="fileName" help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_folderlistDbx = subparser.add_parser("ls:f/Dropbox", help="List Files inside DropBox Folder.")
    sub_parser_folderlistDbx.add_argument("fileName")
    sub_parser_folderlistDbx.add_argument("credential")
    #sub_parser_folderlistDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_delete = subparser.add_parser("rm", help="Delete Files.")
    sub_parser_delete.add_argument("fileName")
    sub_parser_delete.add_argument("credential")
    #sub_parser_deleteDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_download = subparser.add_parser("download", help="Download Files.")
    sub_parser_download.add_argument("fileName")
    sub_parser_download.add_argument("credential")
    #sub_parser_downloadDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_transfer = subparser.add_parser("transfer", help="Transfer Files.")
    sub_parser_transfer.add_argument("fileName")
    sub_parser_transfer.add_argument('-src', dest='credential1', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transfer.add_argument('-dest', dest='credential2', help='user.  If this argument is not passed it will be requested.')
    
    args = parser.parse_args()
    args.funct(args)


def getInstance(endpt):
    if(endpt=='dropbox'):
        instance=dropbox()
    elif(endpt=='gdrive'):
        instance=gdrive()
    elif(endpt=='box'):
        instance=box()
        
    return instance
    
def list(credential):
    if not credential:
        credential=input('UUID:')
        
    endpt,credential = credential.split('://', 1)
    
    obj=getInstance(endpt)
    obj.credentialId=credential
    obj.printlist()
    
def mkdir(credential,fileName):
    if not credential:
        credential=input('UUID:')
    if not fileName:
        fileName=input('Enter FileName to be Created:')
    
    endpt,credential = credential.split('://', 1)
    
    instance=getInstance(endpt)
    instance.credentialId=credential
    instance.mkdir(fileName)
    
def folderlist(credential,fileName):
    if not credential:
        credential=input('UUID:')
    if not fileName:
        fileName=input('Enter Folder Name to be listed:')
        
    endpt,credential = credential.split('://', 1)
    
    instance=getInstance(endpt)
    instance.credentialId=credential
    instance.folderfiles(fileName)
    
def delete(credential,fileName):
    if not credential:
        credential=input('UUID:')
    
    
    endpt,credential = credential.split('://', 1)
    
    instance=getInstance(endpt)
    instance.credentialId=credential
    instance.delete(fileName)
    
def download(credential,fileName):
    if not credential:
        credential=input('UUID:')

    endpt,credential = credential.split('://', 1)
    
    instance=getInstance(endpt)
    instance.credentialId=credential
    instance.download(fileName)
    
def transfer(credential,dest,fileName):
    if not credential:
        credential=input('Dropbox UUID:')
    if not dest:
        dest=input('GoogleDrive UUID:')
    
    endpt,credential = credential.split('://', 1)
    
    instance=getInstance(endpt)
    instance.credentialId=credential
    instance.dest=dest
    instance.transfer(fileName)

    
def main():
    pass

if __name__ == '__main__':
            
        parse_args()
