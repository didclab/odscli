#!/opt/homebrew/bin/python3
"""OneDataShare CLI for interacting with onedatashare.org or directly to your local transfer-service/vfs-node/data-mover

Usage:
  onedatashare.py login [--user=<USER> --password=<PWD> -H HOST]
  onedatashare.py logout
  onedatashare.py addRemote (<user> <host> <type>) [--pass=<pass> --keyfile=<keyfile> --credentialId=<credId>]
  onedatashare.py rmRemote (<credId> <type>)
  onedatashare.py lsRemote <type>
  onedatashare.py (ls | rm | mkdir) <credId> <type> [--path=<path>] [--toDelete=<DELETE>] [--folderToCreate=<DIR>][--jsonprint]
  onedatashare.py transfer (<source_type> <source_credid> <source_path> (-f FILES)... <dest_type> <dest_credid> <dest_path>) [--concurrency=<CONCURRENCY>, --pipesize=<PIPE_SIZE>, --parallel=<PARALLEL>, --chunksize=<CHUNK_SIZE>, --compress=<COMPRESS>, --encrypt=<ENCRYPT>, --optimize=<OPTIMIZE>, --overwrite=<OVERWRITE>, --retry=<RETRY>, --verify=<VERIFY>]
  onedatashare.py query [--job_id=<JOB_ID> | --start_date=<START_DATE> | (--start_date=<START_DATE>  --end_date=<END_DATE>) | --all | --list_job_ids] [--batch_job_only=<BATCH_ONLY> | --measurement_only=<MEASURE_ONLY>]
  onedatashare.py monitor [--job_id=<JOB_ID> --delta_t=<DELTA_T> --experiment_file=<EXP_FILE>]
  onedatashare.py --version

Commands:
    addRemote       Adds a remote server to onedatashare. Currently the CLI does not support any OAuth endpoints. Please use onedatashare.org to add the OAuth services
    lsRemote        List the servers added to onedatashare of a specific protocol <type>
    rmRemote        Deletes a credential that has been added to onedatashare. Requires a type and credential Id.
    ls              List operation on a server that has been added to onedatashare. This requires a credential Id and a type, the path is optional.
    rm              Remove operation on an added server. Requires a credential Id, type, and a path(either folder or file). If a directory is passed then it will recursively delete the directory
    mkdir           Creates a directory on an added server. This requires credential Id, type, and a path to create
    transfer        Submits a transfer job to onedatashare.org. Requires a Source(credentialID, type, source path, list of files), Destination(type, credential ID, destination path). The Transfer options are the following: compress, optimize(inprogress), encrypt(in-progress), overwrite(in-progress), retry, verify, concurrencyThreadCount(server and protocol restrictions apply), parallelThreadCount(not supported on protocols that dont support seek()), pipeSize, chunkSize,
    query           Queries onedatashare for the metrics of a given job that has been submitted. Requires a job id at least.
    monitor         Monitors the given list of job ids. Which means it downloads and displays the data and consumes the terminal till all jobs are done. It defaults to using the last job id in case no job id is specified
    login           Executes the login with the required parameters, if that fails will attempt to use env variables ODS_CLI_USER, ODS_CLI_PWD.

Options:
  -h --help         Show this screen.
  -v, --version     Show version.
  --user=<USER>     The username to use for login
  --password=<PWD>  The password to use for login
  -H HOST           The host of the onedatashare deployment [default: onedatashare.org]
  --credId          A string flag representing the  credential Id for adding removing or listing from an endpoint that has been added already
  --type            A string flag with the possible types: dropbox, gdrive, sftp, ftp, box, s3, http, vfs, scp
  --jsonprint       A boolean flag to print out the response in json [default: ""]
  --path=<path>     A string that is the parent of all the resources we are covering in the operation. Many times this can be empty [default: ]
  --concurrency=<CONCURRENCY>   The number of concurrent connections you wish to use on your transfer [default: 1]
  --pipesize=<PIPE_SIZE>        The amount of reads or writes to do Ex: when 1, read once write once. Ex when 5 read 5 times and write 5 times. [default: 10]
  --parallel=<PARALLEL>         The number of parallel threads to use for every concurrent connection [default: 1]
  --chunksize=<CHUNK_SIZE>      The number of bytes for every read operation default is 64MB [default: 64000000]
  --compress=<COMPRESS>         A boolean flag that will enable compression. This currently only works for SCP, SFTP, FTP. [default: False]
  --encrypt=<ENCRPTY>           A boolean flag to enable encryption. Currently not supported [default: False]
  --optimize=<OPTIMIZE>         A string flag that allows the user to select which form of optimization to use. [default: False]
  --overwrite=<OVERWRITE>       A boolean flag that will overwrite files with the same path as found on the remote. Generally I would not use this. [default: False]
  --retry=<RETRY>               An integer that represents the number of retries for every single file. Generally I would keep this below 10. [default: 5]
  --verify=<VERIFY>             A boolean flag to flag the use of checksumming after every file or after the whole job. [default: False]
  --job_id=<JOB_ID>             A job id to query for and all data that occurred during that job.
  --start_date=<START_DATE>     If used alone then the query will get all jobs launched at said time.
  --end_date=<END_DATE>         Used to determine the second point on the line to query all jobs between start and end.
  --batch_job_only=<BATCH_JOB_ONLY>     A flag that tells the cli to disable querying for job parameter information [default: True]
  --measurement_only=<MEASUREMENT_ONLY>     A flag that tells the cli to disable querying for time series measurements. [default: True]
  --delta_t=<DELTA_T>       A flag that has a time interval to poll monitoring. [default: 10s]
  --all     Will download all of the respective data associated with the measurement, and batch flags. [default: False]
  --list_job_ids    Will list all of the jobIds associated to the user [default: False]
  --experiment_file=<EXP_FILE>      The file to dump all timings of a running job
"""

from docopt import docopt
import os
import json
from datetime import datetime
import sdk.token_utils as tokUt
from sdk.credential_service import CredService as CredS
from sdk.endpoint import Endpoint as endpoint, EndpointType
from sdk.transfer import TransferRequest
from sdk.transfer import TransferOptions
from sdk.transfer import Source
from sdk.transfer import Destination
from sdk.transfer import Iteminfo
from sdk.transfer import Transfer as Transfer
from sdk.meta_query_gui import QueryGui
from pytimeparse.timeparse import timeparse


def login(host, user, password):
    work, tok = tokUt.login(host=host, user=user, password=password)
    if work:
        print("\nSuccessfully Logged In!\n")
        return
    else:
        print("\nProblem Logging In trying to use env variables ODS_CLI_USER and ODS_CLI_PWD\n")
        print(
            "\n If you have a complicated password like it has \! or general complex characters i would advise you use the env variable approach")
    ODS_CLI_USER = os.getenv("ODS_CLI_USER")
    ODS_CLI_PWD = os.getenv("ODS_CLI_PWD")
    work, tok = tokUt.login(host=host, user=ODS_CLI_USER, password=ODS_CLI_PWD)
    if work:
        print("\nSuccessfully Logged In!\n")
        return
    else:
        print(
            "\nProblem Logging In try signing in on https://onedatashare.org to make sure your credentials are accurate\n")


def logout():
    tokUt.logout()
    print("\nLogged Out\n")


def addRemote(remoteHost, remoteUser, remotePassword, keyfile, type, credId):
    host, user, token = tokUt.readConfig()
    try:
        typeE, isOAuth = endpoint.type_handle(type)
    except:
        print("Type Error")
        return
    if isOAuth:
        CredS.oauth_Url(host, typeE, token)
    else:
        # First, check to make sure both are not none.
        if keyfile != None and keyfile != "":
            print("Used the keyfile")
            with open(keyfile, "r") as f:
                keyfile = f.read()
            CredS.register_Credential(host, typeE, credId, remoteHost, remoteUser, keyfile, token)
        else:
            print("Used the password")
            CredS.register_Credential(host, typeE, credId, remoteHost, remoteUser, remotePassword, token)


def listRemote(type):
    host, user, token = tokUt.readConfig()
    res = CredS.get_CredentialODS(type, token, host)  # Needs to be handled better for errors
    print("Remotes:\n")
    for cred in res["list"]:
        print("\t" + cred)
    return res["list"]


def deleteRemote(type, credId):
    host, user, token = tokUt.readConfig()
    res = CredS.delete_CredentialODS(type, credId, token, host)  # Needs to be handled better for errors
    if res.status_code != 200:
        print("error with deleting")
    elif res.status_code == 200:
        print("Credential Deleted")


def ls(type, credId, path):
    host, user, token = tokUt.readConfig()
    jsonstr = endpoint.list(credId=credId, path=path, id=path, host=host, type=type,
                            atok=token)  # Needs to be handled better for errors
    jsonOb = json.loads(jsonstr)  # Needs to be handled better for errors
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
    formating = "{}\t{:>" + str(pad) + "}\t{}\t{}\t.({})\t{}\n"
    print(formating.format(diction.get('permissions'), diction.get('size'), datetime.fromtimestamp(diction.get('time')),
                           diction.get('dir'), diction.get('name'), diction.get('id')))
    diction = diction.get('files')
    if args['--jsonprint']:
        print(json.dumps(jsonOb))
    else:
        for names in diction:
            formating = "{}\t{:>" + str(pad) + "}\t{}\t{}\t{:>" + str(padN) + "}\t{}\n"
            print(
                formating.format(names.get('permissions'), names.get('size'), datetime.fromtimestamp(names.get('time')),
                                 names.get('dir'), names.get('name'), names.get('id')))


def rm(type, credId, toDelete, path=""):
    if toDelete is None:
        print(
            "You did not specify a directory to make. You probably used the --path flag but please the --toDelete flag instead. The --path flag is for the id/path to the parent directory")
        return

    host, user, token = tokUt.readConfig()
    res = endpoint.remove(credId=credId, path=path, id=path, host=host, type=type, atok=token, toDelete=toDelete)
    if res.status_code != 200:
        print("Unable to delete " + toDelete + "\n The error status is " + str(res.status_code))
    elif res.status_code == 200:
        print("Deleted " + toDelete)
    print(res.text)


def mkdir(type, credId, dirToMake, path=""):
    if dirToMake is None:
        print(
            "You did not specify a directory to make. You probably used the --path flag but please the --folderToCreate flag instead. The --path flag is for the id/path to the parent directory")
        return
    if str(type) == EndpointType.S3.value:
        print(
            'S3 does not support making directories. Please the directory you wish your files to end up in as the prefix for your destination. As folders are just files with a common prefix')
        return
    host, user, token = tokUt.readConfig()
    res = endpoint.mkdir(credId=credId, path=path, id=path, host=host, type=type, atok=token, folderToCreate=dirToMake)
    if res.status_code != 200:
        print("Unable to mkdir " + dirToMake + "\n The error status is " + str(res.status_code))
        print(res.text)
    elif res.status_code == 200:
        print("Directory created " + dirToMake)
    print(res)


# <source_type> <source_credid> <source_path> -f FILE... <dest_type> <dest_credid> <dest_path>) [--concurrency, --pipesize, --parallel, --chunksize, --compress, --encrypt, --optimize, --overwrite, --retry, --verify
def transfer(source_type, source_credid, file_list, dest_type, dest_credid, source_path="", dest_path="", concurrency=1,
             pipesize=10, parallel=0, chunksize=10000000, compress=False, encrypt=False, optimize="", overwrite=False,
             retry=5, verify=False):
    host, user, token = tokUt.readConfig()
    infoList = []
    for f in file_list:
        infoList.append(Iteminfo(path=f, id=f, size=0, chunk_size=chunksize))

    source = Source(infoList=infoList, type=source_type, credentialId=source_credid,
                    parentInfo=Iteminfo(source_path, source_path, 0))
    destination = Destination(type=dest_type, credentialId=dest_credid, parentInto=Iteminfo(dest_path, dest_path, 0))
    transferOptions = TransferOptions(concurrency, pipesize, chunksize, parallel, compress, encrypt, optimize,
                                      overwrite, retry, verify)
    transferRequest = TransferRequest(source=source, dest=destination, TransfOp=transferOptions)
    print('Sending Transfer Request: ', transferRequest)
    r = Transfer.transfer(host, token, transferRequest)

    print("status code: " + str(r.status_code))
    print(r.text)


def transfernode_direct(source_type, source_credid, file_list, dest_type, dest_credid, source_path="", dest_path="",
                        concurrency=1, pipesize=10, parallel=0, chunksize=64000, compress=False, encrypt=False,
                        optimize="", overwrite=False, retry=5, verify=False):
    source = Source(infoList=file_list, type=source_type, credentialId=source_credid,
                    parentInfo=Iteminfo(source_path, source_path))


# ( <source_credid> <source_path> (-f FILE)... <dest_type> <dest_credid> <dest_path>)
def main():
    args = docopt(__doc__, version='OneDataShare 0.0.1')
    if args['login']:
        user = args["--user"] if "--user" in args else ""
        password = args["--password"] if "--password" in args else ""
        login(host=args["-H"], user=user, password=password)
    elif args['logout']:
        logout()
    elif args['addRemote']:
        credId = args['<user>'] + "@" + args['<host>']
        if (args['--credentialId'] != None):
            credId = args['--credentialId']
        addRemote(remoteHost=args['<host>'], remoteUser=args['<user>'], remotePassword=args['--pass'],
                  keyfile=args['--keyfile'], credId=credId, type=args['<type>'])
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
        # onedatashare.py transfer [--concurrency, --pipesize, --parallel, --chunksize, --compress, --encrypt, --optimize, --overwrite, --retry, --verify]
        transfer(source_type=args['<source_type>'], source_credid=args['<source_credid>'],
                 source_path=args['<source_path>'], file_list=args['FILES'], dest_type=args['<dest_type>'],
                 dest_credid=args['<dest_credid>'], dest_path=args['<dest_path>'], concurrency=args['--concurrency'],
                 chunksize=args['--chunksize'],
                 parallel=args['--parallel'], compress=args['--compress'], encrypt=args['--encrypt'],
                 optimize=args['--optimize'], overwrite=args['--overwrite'], retry=args['--retry'],
                 verify=args['--verify'], pipesize=args['--pipesize'])

    elif args['query']:
        qg = QueryGui()
        job_id = args['--job_id']
        start_date = args['--start_date']
        end_date = args['--end_date']
        batch_job_only = args['--batch_job_only']
        measurement_only = args['--measurement_only']
        all_jobs = bool(args['--all'])
        list_job_ids = bool(args['--list_job_ids'])
        qg.get_data(job_id=job_id, end_date=end_date, start_date=start_date,
                    influx_only=bool(measurement_only), cdb_only=bool(batch_job_only), all=all_jobs,
                    list_job_ids=list_job_ids)
    elif args['monitor']:
        qg = QueryGui()
        job_id = args['--job_id']
        delta_t = args['--delta_t']
        file_to_dump_times = args['--experiment_file']
        qg.monitor(job_id, int(timeparse(delta_t)), file_to_dump_times)

if __name__ == '__main__':
    main()