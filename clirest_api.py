import argparse, getpass
import requests
import json

def parse_args():
    parser = argparse.ArgumentParser(description="ODS")
    subparser = parser.add_subparsers(dest='command', metavar='command')
    subparser.required = True
    parser.set_defaults(funct=argparser_handler)

    # Login
    sub_parser = subparser.add_parser("login", help="Login with email and password")
    sub_parser.add_argument('-u', dest='user', help='user.  If this argument is not passed it will be requested.')
    sub_parser.add_argument('-p', dest='password', help='password.  If this argument is not passed it will be requested.')
    
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
    
    sub_parser_listGdrive = subparser.add_parser("listGdrive", help="get GoogleDrive Files.")
    sub_parser_listGdrive.add_argument('-cred', dest='credential', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_transferDbxtoGdrive = subparser.add_parser("transferDbxtoGdrive", help="Transfer Files.")
    sub_parser_transferDbxtoGdrive.add_argument('-src', dest='credential1', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-dest', dest='credential2', help='user.  If this argument is not passed it will be requested.')
    sub_parser_transferDbxtoGdrive.add_argument('-file', dest='fileName', help='user.  If this argument is not passed it will be requested.')
    
    sub_parser_queue = subparser.add_parser("queue", help="Get Queue.")

    args = parser.parse_args()
    args.funct(args)

def argparser_handler(args):
    if (args.command == 'login'):
        login(args.user, args.password)
    elif (args.command == 'listDbx'):
        getDbxList(args.credential)
    elif (args.command == 'queue'):
        getQueue()
    elif (args.command == 'mkdirDbx'):
        mkdirDbx(args.credential,args.fileName)
    elif (args.command == 'folderlistDbx'):
        folderlistDbx(args.credential,args.fileName)
    elif (args.command == 'deleteDbx'):
        deleteDbx(args.credential,args.fileName)
    elif (args.command == 'listGdrive'):
        getGdriveList(args.credential)
    elif (args.command == 'transferDbxtoGdrive'):
        transferDbxtoGdrive(args.credential1,args.credential2,args.fileName)    
    

token=''


def login(user, password):
    if not user:
        user = input("User:") 
    if not password:
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
        print(response['token']) 
        print(req.content)
        token=response['token']
               
    return token

def getDbxList(credential):
    if not credential:
        credential = input("DropBox Account:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
    "uri": "dropbox:///",
    "id": None,
    "credential": {
        "name": credential,
        "tokenSaved": False,
        "token": "HcMXTiTtgesAAAAAAAAA4Qt-abaLywfk4d9-nmvSoFCAt4lJ3UED7IWTjkNdDNas"
    }
    }
    
    
    with requests.Session() as s:
        url="http://localhost:8080/api/dropbox/ls"         
        req=s.post(url,data=json.dumps(data),headers=headers)
        response=json.loads(req.content)
        for file in response['files']:
            print(file['name']) 
            
        
        
def mkdirDbx(credential,fileName):
    if not credential:
        credential = input("DropBox Account:")
    if not fileName:
        fileName = input("FileName:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
	"credential":{
		"name":"credential",
		"tokenSaved":False,
		"token":"HcMXTiTtgesAAAAAAAAA4Qt-abaLywfk4d9-nmvSoFCAt4lJ3UED7IWTjkNdDNas"
        },
		"uri":"dropbox:///"+fileName,
		"id":None,
		"map":[{
			"id":None,
			"path":"dropbox:///"}]

    }
 
    print(data) 
    
    with requests.Session() as s:
        url="http://localhost:8080/api/dropbox/mkdir"            
        req=s.post(url,data=json.dumps(data),headers=headers)
        print(req.content) 
        print(req.status_code)
   

def folderlistDbx(credential,fileName):
    if not credential:
        credential = input("DropBox Account:")
    if not fileName:
        fileName = input("FileName:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
    
	"credential":{
		"name":"credential",
		"tokenSaved":False,
		"token":"HcMXTiTtgesAAAAAAAAA4Qt-abaLywfk4d9-nmvSoFCAt4lJ3UED7IWTjkNdDNas"
        },
		"uri":"dropbox:///"+fileName
		

    }
    
    with requests.Session() as s:
        url="http://localhost:8080/api/dropbox/ls"         
        req=s.post(url,data=json.dumps(data),headers=headers)
        response=json.loads(req.content)
        if len(response['files']) == 0:
            print("No files Found")
        else :
            for file in response['files']:
                print(file['name'])
                
                
def deleteDbx(credential,fileName):
    if not credential:
        credential = input("DropBox Account:")
    if not fileName:
        fileName = input("FileName:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
    
	"credential":{
		"name":"credential",
		"tokenSaved":False,
		"token":"HcMXTiTtgesAAAAAAAAA5s2ypub-9ClCuYEdLCgslxls5LQ99PznDc1KCZobV3D8"
        },
		"uri":"dropbox:///"+fileName,
		"map":[{
			"id":None,
			"path":"dropbox:///"}]
		
    }
    
    with requests.Session() as s:
        url="http://localhost:8080/api/dropbox/rm"         
        req=s.post(url,data=json.dumps(data),headers=headers)
        print(req.content) 
        print(req.status_code)
    
    
def getGdriveList(credential):
    if not credential:
        credential = input("GoogleDrive Account:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
    
	"credential":{
		"name":"credential",
		"tokenSaved":False,
		"token":"ya29.a0Adw1xeV5xaBqlOx9HyXUKh7j9ILhOyyOCOjFa_C800UP5ElveYGvDpwQKDWU02DZ4yFI1JrCql_1I7IpIJ4nQBuRG9_YaJ6g95muminHkKFWqM-uAEWbWTlMnmOwEqMwF88cxqpd4zOEj34HsbLo1J_1v9DREvinAcg"
        },
        
		"uri":"googledrive:/"
		
    }
    
    with requests.Session() as s:
        url="http://localhost:8080/api/googledrive/ls"         
        req=s.post(url,data=json.dumps(data),headers=headers)
        response=json.loads(req.content)
        for file in response['files']:
            print(file['name']) 
            
            
def transferDbxtoGdrive(credential1,credential2,fileName):
    if not credential1:
        credential1 = input("Source Account:")
    if not credential2:
        credential1 = input("Destination Account:")
    if not fileName:
        fileName = input("FileName:")
        
    
    headers={
    'content-type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    
    data={
    "src":{
    "credential":{
        "name":"credential1",
        "tokenSaved":False,
        "token":"HcMXTiTtgesAAAAAAAACFnMD0RSHxIq98VikvWEqx-_-axXNz_RmfIaY6-KRnybW"
        },
        "uri":"dropbox:///"+fileName,
        "type":"dropbox:///",
        "map":[{"id":None,"path":"dropbox:///"}]
        },
        
    "dest":{
    "credential":{
        "name":"credential2",
        "tokenSaved":False,
        "token":"ya29.a0Adw1xeV5xaBqlOx9HyXUKh7j9ILhOyyOCOjFa_C800UP5ElveYGvDpwQKDWU02DZ4yFI1JrCql_1I7IpIJ4nQBuRG9_YaJ6g95muminHkKFWqM-uAEWbWTlMnmOwEqMwF88cxqpd4zOEj34HsbLo1J_1v9DREvinAcg"},
        "id":None,
        "uri":"googledrive:/"+fileName,
        "type":"googledrive:/",
        "map":[{"id":None,"path":"googledrive:/"}]
        },
        
    "options":{
        "optimizer":"None",
        "overwrite":True,
        "verify":True,
        "encrypt":True,
        "compress":True,
    "retry":5
        }	
    }
    
    with requests.Session() as s:
        url="http://localhost:8080/api/stork/submit"         
        req=s.post(url,data=json.dumps(data),headers=headers)
        print(req.content) 
        print(req.status_code)
    
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
        
    parse_args()
    main()

