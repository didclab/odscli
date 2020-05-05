#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from endpoint.Dropbox import dropbox
from endpoint.Gdrive import gdrive
from endpoint.Endpoint import endpoint


def argparser_handler(args):
    if(args.command=='ls/Dropbox'):
        if(args.fileName==None):
            dbxList(args.credential)
        else:
            folderlistDbx(args.credential,args.fileName)
    elif(args.command=='ls/Gdrive'):
        gdriveList(args.credential)
    elif(args.command=='mkdir/Dropbox'):
        dirDbx(args.credential,args.fileName)
    elif (args.command == 'ls:f/Dropbox'):
        folderlistDbx(args.credential,args.fileName)
    elif (args.command == 'rm/Dropbox'):
        deleteDbx(args.credential,args.fileName)
    elif (args.command == 'DbxtoGdrive'):
        DbxtoGdrive(args.credential1,args.credential2,args.fileName)
        
def parse_args():
    parser = argparse.ArgumentParser(description="ODS")
    
 
    subparser = parser.add_subparsers(dest='command', metavar='command')
    subparser.required = True
    parser.set_defaults(funct=argparser_handler)
    
    sub_parser_listDbx = subparser.add_parser("ls/Dropbox", help="List DropBox Files and Folders.")
    sub_parser_listDbx.add_argument('-f', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    sub_parser_listDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_mkdirDbx = subparser.add_parser("mkdir/Dropbox", help="Make DropBox Folder.")
    sub_parser_mkdirDbx.add_argument("fileName")
    #sub_parser_mkdirDbx.add_argument("credential")
    
    
    #parser.add_argument('string', help='Input String', nargs='+', action=dirDbx)
    sub_parser_mkdirDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    #sub_parser_mkdirDbx.add_argument('file', metavar="fileName" help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_folderlistDbx = subparser.add_parser("ls:f/Dropbox", help="List Files inside DropBox Folder.")
    sub_parser_folderlistDbx.add_argument("fileName")
    sub_parser_folderlistDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_deleteDbx = subparser.add_parser("rm/Dropbox", help="Delete DropBox Files.")
    sub_parser_deleteDbx.add_argument("fileName")
    sub_parser_deleteDbx.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    
    sub_parser_transferDbxtoGdrive = subparser.add_parser("DbxtoGdrive", help="Transfer Files.")
    sub_parser_transferDbxtoGdrive.add_argument('-src', dest='credential1', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-dest', dest='credential2', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_listGdrive = subparser.add_parser("ls/Gdrive", help="List DropBox Files and Folders.")
    sub_parser_listGdrive.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    args = parser.parse_args()
    args.funct(args)
    
def dbxList(credential):
    if not credential:
        credential=input('UUID:')

    instance1=dropbox()
    instance1.credentialId=credential
    instance1.list()
    
def dirDbx(credential,fileName):
    if not credential:
        credential=input('UUID:')
    if not fileName:
        fileName=input('Enter FileName to be Created:')
    
    instance2=dropbox()
    instance2.credentialId=credential
    instance2.mkdir(fileName)
    
def folderlistDbx(credential,fileName):
    if not credential:
        credential=input('UUID:')
    if not fileName:
        fileName=input('Enter Folder Name to be listed:')
    
    instance3=dropbox()
    instance3.credentialId=credential
    instance3.folderfiles(fileName)
    
def deleteDbx(credential,fileName):
    if not credential:
        credential=input('UUID:')
    if not fileName:
        fileName=input('Enter File to be deleted:')
    
    instance4=dropbox()
    instance4.credentialId=credential
    instance4.delete(fileName)
    
def DbxtoGdrive(credential,credential1,credential2,fileName):
    if not credential:
        credential=input('UUID:')
    if not credential1:
        credential1=input('DropBox Account:')
    if not credential2:
        credential2=input('GoogleDrive Account:')
    if not fileName:
        fileName=input('Enter File to be transferred:')
    
    instance5=dropbox()
    instance5.credentialId=credential
    instance5.transfer(credential1,credential2,fileName)
    
def gdriveList(credential):
    if not credential:
        credential=input('UUID:')

    instance6=gdrive()
    instance6.credentialId=credential
    instance6.list()
    
def main():
    pass

if __name__ == '__main__':
            
        parse_args()