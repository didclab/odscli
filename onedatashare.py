"""OneDataShare CLI for interacting with onedatashare.org or directly to your local transfer-service/vfs-node/data-mover
Things to know when writing:
<> = WORDSINCAPS    stand for arguments and do not require flags just write the values in order
[]                  stand for optional arguments or anything within the braces is optional
--                  According to POSIX std all arguments are positional arguments even tho they might look like options
-                   Program will take input from std input vs from file. Not hard std of POSIX
To do any kind of OAuth endpoints such as: Google Drive, Dropbox, Box, GridFTP please add credential through onedatashare.org directly

Usage:
  onedatashare.py login <user> <password> [-H HOST]
  onedatashare.py logout
  onedatashare.py addRemote (<user> (--pass=<pass> | --keyfile=<keyfile>) <host> <type>) [--credentialId=<credId>]
  onedatashare.py rmRemote (<credId> <type>)
  onedatashare.py lsRemote <type>
  onedatashare.py (ls | rm | mkdir) <credId> <type> [--path=<path>] [--toDelete=<DELETE>] [--folderToCreate=<DIR>][--jsonprint]
  onedatashare.py transfer (<source_type> <source_credid> <source_path> (-f FILES)... <dest_type> <dest_credid> <dest_path>) [--concurrency, --pipesize, --parallel, --chunksize, --compress, --encrypt, --optimize, --overwrite, --retry, --verify, --test=<times>]
  onedatashare.py testAll (<source_type> <source_credid> <source_path> (-f FILES)... <dest_path>) [--repeat=<times>]
  onedatashare.py query <jobId>
  onedatashare.py rc_transfer <source_credid> <source_path> <file> <dest_credid> <dest_path> [--process --repeat=<times> --all]
  onedatashare.py rc_delete <source_credid> <path> <file> [--all]
  onedatashare.py rc_lsRemote
  onedatashare.py --version
  onedatashare.py help <command>

Commands:
    addRemote       Adds a remote server to onedatashare. Currently the CLI does not support any OAuth endpoints. Please use onedatashare.org to add the OAuth services
    lsRemote        List the servers added to onedatashare of a specific protocol <type>
    rmRemote        Deletes a credential that has been added to onedatashare. Requires a type and credential Id.
    ls              List operation on a server that has been added to onedatashare. This requires a credential Id and a type, the path is optional.
    rm              Remove operation on an added server. Requires a credential Id, type, and a path(either folder or file). If a directory is passed then it will recursively delete the directory
    mkdir           Creates a directory on an added server. This requires credential Id, type, and a path to create
    transfer        Submits a transfer job to onedatashare.org. Requires a Source(credentialID, type, source path, list of files), Destination(type, credential ID, destination path). The Transfer options are the following: compress, optimize(inprogress), encrypt(in-progress), overwrite(in-progress), retry, verify, concurrencyThreadCount(server and protocol restrictions apply), parallelThreadCount(not supported on protocols that dont support seek()), pipeSize, chunkSize, test
    query           Queries onedatashare for the metrics of a given job that has been submitted. Requires a job id at least.
    testAll         Submit a transfer job with test purpose to all existing credential id
    rc_transfer     Use rClone to submit a transfer from one remote to another remote
    rc_delete       Use rClone to delete specifc file that existing in the remote
    rc_lsRemote     List the existing remotes in the rclone
    help            Give the document about specific command include: example, usage, description

Options:
  -h --help                 Show this screen.
  -v, --version             Show version.
  -H HOST                   The host of the onedatashare deployment [default: onedatashare.org]
  --credId                  A string flag representing the  credential Id for adding removing or listing from an endpoint that has been added already
  type                      A string flag with the possible types: dropbox, gdrive, sftp, ftp, box, s3, gftp(pending), http, vfs, scp
  --jsonprint               A boolean flag to print out the response in json [default: ""]
  --path=<path>             A string that is the parent of all the resources we are covering in the operation. Many times this can be empty [default: ]
  --concurrency             The number of concurrent connections you wish to use on your transfer [default: 1]
  --pipesize                The amount of reads or writes to do Ex: when 1, read once write once. Ex when 5 read 5 times and write 5 times. [default: 10]
  --parallel                The number of parallel threads to use for every concurrent connection
  --chunksize               The number of bytes for every read operation default is 64KB [default: 64000]
  --compress                A boolean flag that will enable compression. This currently only works for SCP, SFTP, FTP. [default: False]
  --encrypt                 A boolean flag to enable encryption. Currently not supported [default: False]
  --optimize                A string flag that allows the user to select which form of optimization to use. [default: False]
  --overwrite               A boolean flag that will overwrite files with the same path as found on the remote. Generally I would not use this [default: False]
  --retry                   An integer that represents the number of retries for every single file. Generally I would keep this below 10 [default: 5]
  --verify                  A boolean flag to flag the use of checksumming after every file or after the whole job. [default: False]
  --test=<test_times>       An integer that represents the number of tests that you wish to transfer this file to destination. [default: 1]
  --repeat=<repeat_times>   An integer to represents the number of testAll will run. [default: 1]
  --process                 Shows up live process for transfer (rc_command only) [default: False]
  --all                     Make transfer from one to one to be one to all (existing remote) [default: False]
  command                   shows commands [default: ]

Example:
  onedatashare.py help [command]        For more information about command
"""

from asyncore import file_dispatcher
from docopt import docopt
import os
import json
import pprint
import requests
from datetime import datetime
import subprocess
#SDK IMPORTS
import SDK.token_utils as tokUt
from SDK.credential_service import CredService as CredS
import SDK.endpoint
from SDK.endpoint import Endpoint as endpoint, EndpointType
from SDK.transfer import TransferRequest
from SDK.transfer import TransferOptions
from SDK.transfer import Source
from SDK.transfer import Destination
from SDK.transfer import Iteminfo
from SDK.transfer import Transfer as Transfer



def login(host, user, password):
  work, tok = tokUt.login(host=args['-H'], user=args['<user>'], password=args['<password>'])
  if work:
      print("\nSuccessfully Logged In!\n")
  else:
      print("\nProblem Logging In\n")

def logout():
  tokUt.logout()
  print("\nLogged Out\n")

def addRemote(remoteHost, remoteUser, remotePassword, keyfile, type, credId):
    host,user,token = tokUt.readConfig()
    try:
        typeE,isOAuth = endpoint.type_handle(type)
    except:
        print("Type Error")
        return
    if isOAuth:
        CredS.oauth_Url(host,typeE,token)
    else:
        # First, check to make sure both are not none.
        if keyfile == "" and remotePassword == "":
            print("Password Error: No password given")
        elif keyfile != None and remotePassword != None:
            print("Password Error: Both password types given, please only provide one")
        else:
            if keyfile != None and keyfile != "":
                print("Used the keyfile")
                with open(keyfile, "r") as f:
                    keyfile = f.read()
                CredS.register_Credential(host,typeE, credId, remoteHost,remoteUser,keyfile,token)                
            else:
                print("Used the password")
                CredS.register_Credential(host,typeE,credId,remoteHost,remoteUser,remotePassword,token)

def listRemote(type):
    host,user,token = tokUt.readConfig()
    res = CredS.get_CredentialODS(type,token,host) # Needs to be handled better for errors
    print("Remotes:\n")
    for cred in res["list"]:
        print("\t"+cred)
    return res["list"]

def deleteRemote(type, credId):
    host,user,token = tokUt.readConfig()
    res = CredS.delete_CredentialODS(type,credId,token,host)# Needs to be handled better for errors
    if res.status_code != 200:
        print("error with deleting")
    elif res.status_code == 200:
        print("Credential Deleted")

def ls(type, credId, path):
    host,user,token = tokUt.readConfig()
    jsonstr = endpoint.list(credId=credId,path=path,id=path,host=host,type=type,atok=token)# Needs to be handled better for errors
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
    if args['--jsonprint']:
        print(json.dumps(jsonOb))
    else:
        for names in diction:
            formating = "{}\t{:>"+str(pad)+"}\t{}\t{}\t{:>"+str(padN)+"}\t{}\n"
            print(formating.format(names.get('permissions'),names.get('size'),datetime.fromtimestamp(names.get('time')),names.get('dir'),names.get('name'),names.get('id')))

def rm(type, credId, toDelete, path=""):
    if toDelete is None:
          print("You did not specify a directory to make. You probably used the --path flag but please the --toDelete flag instead. The --path flag is for the id/path to the parent directory")
          return
      
    host,user,token = tokUt.readConfig()
    res = endpoint.remove(credId=credId, path=path, id=path, host=host, type=type, atok=token, toDelete=toDelete)
    if res.status_code != 200:
        print("Unable to delete "+toDelete +"\n The error status is " + str(res.status_code))
    elif res.status_code == 200:
        print("Deleted " + toDelete)
    print(res.text)

def mkdir(type, credId, dirToMake, path=""):
    if dirToMake is None:
          print("You did not specify a directory to make. You probably used the --path flag but please the --folderToCreate flag instead. The --path flag is for the id/path to the parent directory")
          return
    if str(type) == EndpointType.S3.value:
          print('S3 does not support making directories. Please the directory you wish your files to end up in as the prefix for your destination. As folders are just files with a common prefix')
          return
    host,user,token = tokUt.readConfig()
    res = endpoint.mkdir(credId=credId, path=path, id=path, host=host, type=type, atok=token, folderToCreate=dirToMake)
    if res.status_code != 200:
        print("Unable to mkdir "+dirToMake +"\n The error status is " + str(res.status_code))
        print(res.text)
    elif res.status_code == 200:
        print("Directory created "+dirToMake)
    print(res)


#<source_type> <source_credid> <source_path> -f FILE... <dest_type> <dest_credid> <dest_path>) [--concurrency, --pipesize, --parallel, --chunksize, --compress, --encrypt, --optimize, --overwrite, --retry, --verify, --test, --testAll
def transfer(source_type, source_credid, file_list, dest_type, dest_credid, source_path="",dest_path="", concurrency=1, pipesize=10, parallel=0, chunksize=64000, compress=False, encrypt=False, optimize="", overwrite=False, retry=5, verify=False, test=1):
    host, user, token = tokUt.readConfig()
    infoList=[]
    for f in file_list:
          infoList.append(Iteminfo(f,f,0))
  
    source = Source(infoList=infoList, type=source_type, credentialId=source_credid, parentInfo=Iteminfo(source_path, source_path, 0))
    destination = Destination(type=dest_type, credentialId=dest_credid, parentInto=Iteminfo(dest_path, dest_path, 0))
    transferOptions = TransferOptions(concurrency, pipesize, chunksize, parallel, compress, encrypt, optimize, overwrite, retry, verify)
    transferRequest = TransferRequest(source=source, dest=destination, TransfOp=transferOptions)

    r = Transfer.transfer(host,token,transferRequest)

    print("status code: "+str(r.status_code))
    print(r.text)

###################################### rClone command method
def lsRcRemotes():
    with subprocess.Popen(["rclone","listremotes"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            (out, err) = process.communicate()
    list = out.decode("utf-8").split("\n")
    return list[:-1]


def rcTransfer(command, source_credid, source_path, file, dest_credid, dest_path, process=False, repeat=1):
    if(source_credid[-1] != ':'):
        source_credid = source_credid+":"
    if(dest_credid[-1] != ':'):
        dest_credid = dest_credid+":"
    arg1 = source_credid+source_path+"/"+file
    arg2 = dest_credid+dest_path
    if process: process = "-P"
    else: process = ""
    print(dest_credid + " -------------------------------------------------------------------------------------------")
    cml = "rclone" + " " + command + " " + arg1 + " " + arg2 + " " + str(process) + " --log-file=log.json --log-level=INFO --use-json-log"
    os.system(cml)
    print(" ")
    return


def checkFile(dest_credid, path, file):
    if(dest_credid[-1] != ':'):
        dest_credid = dest_credid+":"
    arg1 = dest_credid + path
    with subprocess.Popen(["rclone", "lsf",arg1], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            (out, err) = process.communicate()
    file_list = out.decode("utf-8").split("\n")
    for info in file_list:
        if info == file:
            return True
    return False


def deleteFile(command, dest_credid, path, file):
    if(dest_credid[-1] != ':'):
        dest_credid = dest_credid+":"
    target = path + "/" + file
    cml = "rclone" + " " + command + " " + dest_credid + target
    os.system(cml)

      
def parsingAndWirteLog(type1, type2, input, output):
    with open(input, "r+") as f:
        for line in f:
            data = json.loads(line)
            if 'stats' not in data: continue
            stats = data['stats']
            elapsed_time = stats['elapsedTime']
            size = stats['bytes']
            outputFile = open(output, "a+")
            outputFile.write(type1 + " -> " + type2 + ", " + str(size) + ", " + str(elapsed_time))
            outputFile.write("\n")
            outputFile.close()
        f.truncate(0)
    return

# def transfer_handler():
#     """onedatashare.py rc_transfer <source_credid> <source_path> <file> <dest_credid> <dest_path> [--process --repeat=<times> --all]

#     make a transfer from source_credid path to destned
#     """
#     print("Foo, {}".format(args['<name>']))

    
if __name__ == '__main__':
    args = docopt(__doc__, version='OneDataShare 0.9.1')
    print(args)
    if args['help']:
        print("this is " + str(args['[command]']))
    if args['login']:
        login(host=args["-H"], user=args["<user>"], password=args['<password>'])
    elif args['logout']:
          logout()
    elif args['addRemote']:
          credId = args['<user>'] + "@" + args['<host>']
          if(args['--credentialId'] != None):
                credId = args['--credentialId']
          addRemote(remoteHost=args['<host>'], remoteUser=args['<user>'], remotePassword=args['--pass'], keyfile=args['--keyfile'], credId=credId, type=args['<type>'])
    elif args['lsRemote']:
          listRemote(args['<type>'])
    elif args['rmRemote']:
          deleteRemote(args['<type>'], args['<credId>'])
    elif args['ls']:
          ls(args['<type>'], args['<credId>'], args['--path'])
    elif args['rm']:
          rm(type=args['<type>'], credId=args['<credId>'], path=args['--path'], toDelete=args['--toDelete'])
    elif args['mkdir']:
          mkdir(type=args['<type>'], credId=args['<credId>'], path=args['--path'], dirToMake=args['--folderToCreate'])
    elif args['transfer']:
        test_time = 1
        if args['--test'] != None:
          test_time = int(args['--test'])
        for i in range(0, test_time):
          transfer(source_type=args['<source_type>'], source_credid=args['<source_credid>'], source_path= args['<source_path>'], file_list=args['FILES'], dest_type=args['<dest_type>'], dest_credid=args['<dest_credid>'], dest_path=args['<dest_path>']) 
    elif args['query']:
          print('not yet implemented')
    elif args['testAll']:
          endpoint_types = ["box", "dropbox", "s3", "ftp","sftp"]
          t = 1
          if (args['--repeat'] != None): t = int(args['--repeat'])
          s_type, s_credId, s_path, file, path= args['<source_type>'],  args['<source_credid>'], args['<source_path>'], args['FILES'], args['<dest_path>']
          sourceDes_path = {"box": "156757741686", "s3": "", "dropbox": "/"+str(path)+"/"+ file[0]}
          for time in range(0, t):
            for endpoint_type in endpoint_types:
                cred_list = listRemote(endpoint_type)
                for id in cred_list:
                    if s_type!= endpoint_type: 
                        temp = path
                        if endpoint_type in sourceDes_path:
                            path = sourceDes_path[endpoint_type]
                        transfer(source_type=s_type, source_credid=s_credId, source_path= s_path, file_list=file, dest_type=endpoint_type, dest_credid=id, dest_path=path)
                        path = temp
    elif args['rc_transfer']:
        times = int(args["--repeat"])
        p = args["--process"]
        transfer_all = args["--all"]
        source_credid, source_path, file_name, dest_path, dest_credid = args["<source_credid>"], args["<source_path>"], args["<file>"], args["<dest_path>"], args["<dest_credid>"]
        remotes = lsRcRemotes()
        if transfer_all:
            for remote in remotes:
                if remote != source_credid+":":
                    for i in range (0, times):
                        if checkFile(remote, dest_path, file_name): 
                            print("delete file successful")
                            deleteFile("deletefile", remote, dest_path, file_name)
                        rcTransfer("copy", source_credid, source_path, file_name, remote, dest_path, remote, p)
                parsingAndWirteLog(source_credid, remote,"log.json","benchmarking.txt")
        else:
            for i in range (0, times):
                if checkFile(dest_credid, dest_path, file_name): 
                    print("delete file successful")
                    deleteFile("deletefile", dest_credid, dest_path, file_name)
                rcTransfer("copy", source_credid, source_path, file_name, dest_credid, dest_path, dest_credid, p)
            parsingAndWirteLog(source_credid, dest_credid,"log.json","benchmarking.txt")
    elif args['rc_delete']:
        delete_all = args["--all"]
        remotes = lsRcRemotes()
        source, path, file_name = args['<source_credid>'], args['<path>'], args['<file>']
        if delete_all:
            for remote in remotes:
                deleteFile("deletefile", remote, path, file_name)
        else:   
            deleteFile("deletefile",source, path, file_name)
    elif args['rc_lsRemote']:
        print(lsRcRemotes())


#        onedatashare.py addRemote (<user> (--pass=<pass> | --keyfile=<keyfile>)                         <host>       <type>) [--credentialId=<credId>]
#python3 onedatashare.py addRemote   cc     --keyfile=/Users/mengyuan/Downloads/JacobNUChameleon.pem 165.124.33.183:22 sftp   --credentialId=ccNuBench 
#python3 onedatashare.py addRemote   cc     --keyfile=/Users/mengyuan/Downloads/JacobNUChameleon.pem    ccNuBench      sftp   --credentialId=ccNuBench 
