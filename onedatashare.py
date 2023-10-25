#!/opt/homebrew/bin/python3
"""OneDataShare CLI for interacting with onedatashare.org or directly to your local transfer-service/vfs-node/data-mover

Usage:
  onedatashare.py login [--user=<USER> --password=<PWD> -H HOST]
  onedatashare.py logout
  onedatashare.py query [--job_id=<JOB_ID> | --start_date=<START_DATE> | (--start_date=<START_DATE>  --end_date=<END_DATE>) | --all | --list_job_ids] [--batch_job_only=<BATCH_ONLY> | --measurement_only=<MEASURE_ONLY>] [--experiment_file=<EXPERIMENT_FILE>]
  onedatashare.py monitor [--job_id=<JOB_ID> --delta_t=<DELTA_T> --experiment_file=<EXP_FILE> --monitor_direct=<MONITOR_DIRECT>]
  onedatashare.py --version


Commands:
    addRemote       Adds a remote server to onedatashare. Currently the CLI does not support any OAuth endpoints. Please use onedatashare.org to add the OAuth services
    lsRemote        List the servers added to onedatashare of a specific protocol <type>
    rmRemote        Deletes a credential that has been added to onedatashare. Requires a type and credential Id.
    ls              List operation on a server that has been added to onedatashare. This requires a credential Id and a type, the path is optional.
    rm              Remove operation on an added server. Requires a credential Id, type, and a path(either folder or file). If a directory is passed then it will recursively delete the directory
    mkdir           Creates a directory on an added server. This requires credential Id, type, and a path to create
    transfer        Submits a transfer job to onedatashare.org. Requires a Source(credentialID, type, source path, list of files), Destination(type, credential ID, destination path). The Transfer options are the following: compress, optimize(inprogress), encrypt(in-progress), overwrite(in-progress), retry, verify, concurrencyThreadCount(server and protocol restrictions apply), parallelThreadCount(not supported on protocols that dont support seek()), pipeSize, chunkSize,save,   query           Queries onedatashare for the metrics of a given job that has been submitted. Requires a job id at least.
    transfer        Submits a transfer job to onedatashare.org. Requires a config that reads data from configuration file. The Transfer options are the following: compress, optimize(inprogress), encrypt(in-progress), overwrite(in-progress), retry, verify, concurrencyThreadCount(server and protocol restrictions apply), parallelThreadCount(not supported on protocols that dont support seek()), pipeSize, chunkSize,save, config   query           Queries onedatashare for the metrics of a given job that has been submitted. Requires a job id at least.
    monitor         Monitors the given list of job ids. Which means it downloads and displays the data and consumes the terminal till all jobs are done. It defaults to using the last job id in case no job id is specified
    login           Executes the login with the required parameters, if that fails will attempt to use env variables ODS_CLI_USER, ODS_CLI_PWD.

Options:
  -h --help         Show this screen.
  -v, --version     Show version.
  --user=<USER>     The username to use for login [default: ]
  --password=<PWD>  The password to use for login
  --pass=<pass>     The default password for an endpoint [default: ]
  -H HOST           The host of the onedatashare deployment [default: onedatashare.org]
  --credId          A string flag representing the  credential Id for adding removing or listing from an endpoint that has been added already
  --type            A string flag with the possible types: dropbox, gdrive, sftp, ftp, box, s3, http, vfs, scp
  --jsonprint       A boolean flag to print out the response in json [default: ""]
  --path=<path>     A string that is the parent of all the resources we are covering in the operation. Many times this can be empty [default: ]
  --concurrency=<CONCURRENCY>   The number of concurrent connections you wish to use on your transfer [default: 1]
  --pipesize=<PIPE_SIZE>        The amount of reads or writes to do Ex: when 1, read once write once. Ex when 5 read 5 times and write 5 times. [default: 10]
  --parallel=<PARALLEL>         The number of parallel threads to use for every concurrent connection [default: 1]
  --chunksize=<CHUNK_SIZE>      The number of bytes for every read operation default is 64MB [default: 64000000]
  --compress=<COMPRESS>         A boolean flag that will enable compression. This currently only  works for SCP, SFTP, FTP. [default: False]
  --encrypt=<ENCRPTY>           A boolean flag to enable encryption. Currently not supported [default: False]
  --optimize=<OPTIMIZE>         A string flag that allows the user to select which form of optimization to use. [default: False]
  --overwrite=<OVERWRITE>       A boolean flag that will overwrite files with the same path as found on the remote. Generally I would not use this. [default: False]
  --retry=<RETRY>               An integer that represents the number of retries for every single file. Generally I would keep this below 10. [default: 5]
  --verify=<VERIFY>             A boolean flag to flag the use of checksumming after every file or after the whole job. [default: False]
  --save=<SAVE>                 Save the transfer configuration.
  --config=<CONFIG>             Use configuration file to read transfer parameters
  --job_id=<JOB_ID>             A job id to query for and all data that occurred during that job.
  --start_date=<START_DATE>     If used alone then the query will get all jobs launched at said time.
  --end_date=<END_DATE>         Used to determine the second point on the line to query all jobs between start and end.
  --batch_job_only=<BATCH_JOB_ONLY>     A flag that tells the cli to disable querying for job parameter information [default: True]
  --measurement_only=<MEASUREMENT_ONLY>     A flag that tells the cli to disable querying for time series measurements. [default: True]
  --delta_t=<DELTA_T>           A flag that has a time interval to poll monitoring. [default: 5s]
  --all                         Will download all of the respective data associated with the measurement, and batch flags. [default: False]
  --list_job_ids                Will list all of the jobIds associated to the user [default: False]
  --experiment_file=<EXP_FILE>  The file to dump all timings of a running job
  --monitor_direct=<MONITOR_DIRECT> The Transfer Service ip address to monitor JobMetadata from, Influx is through OneDataShare.org
  monitoring interface can be

"""

from docopt import docopt
import os
import json
from datetime import datetime
import sdk.token_utils as tokUt
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

def transfer_config(config_name):
    host, user, token = tokUt.readConfig()
    transfer_config = tokUt.readTransferConfig(user, config_name)
    print('Transfer Config:', transfer_config)

    # Create transfer request
    # transfer_request = TransferRequest()
    # Create transfer request
    source_type = transfer_config.get('source_type', '')
    source_credid = transfer_config.get('source_credid', '')
    source_path = transfer_config.get('source_path', '')
    dest_type = transfer_config.get('dest_type', '')
    dest_credid = transfer_config.get('dest_credid', '')
    dest_path = transfer_config.get('dest_path', '')
    file_list = transfer_config.get('file_list', [])
    concurrency = int(transfer_config.get('concurrency', 1))
    pipesize = int(transfer_config.get('pipesize', 10))
    parallel = int(transfer_config.get('parallel', 0))
    chunksize = int(transfer_config.get('chunksize', 10000000))
    compress = bool(transfer_config.get('compress', False))
    encrypt = bool(transfer_config.get('encrypt', False))
    optimizer = transfer_config.get('optimizer', None)
    overwrite = bool(transfer_config.get('overwrite', False))
    retry = int(transfer_config.get('retry', 5))
    verify = bool(transfer_config.get('verify', False))

    infoList = []
    for f in file_list:
        if len(f) > 0:
            infoList.append(Iteminfo(path=f, id=f, size=0, chunk_size=chunksize))

    source = Source(infoList=infoList, type=source_type, credentialId=source_credid,
                    parentInfo=Iteminfo(source_path, source_path, 0))
    destination = Destination(type=dest_type, credentialId=dest_credid, parentInto=Iteminfo(dest_path, dest_path, 0))
    transferOptions = TransferOptions(concurrency, pipesize, chunksize, parallel, compress, encrypt, optimizer,
                                      overwrite, retry, verify)
    transferRequest = TransferRequest(source=source, dest=destination, TransfOp=transferOptions)

    print('Sending Transfer Request: ', transferRequest)
    r = Transfer.transfer(host, token, transferRequest)

    print("status code: " + str(r.status_code))
    print(r.text)


# ( <source_credid> <source_path> (-f FILE)... <dest_type> <dest_credid> <dest_path>)
if __name__ == '__main__':
    args = docopt(__doc__, version='OneDataShare 0.0.1')
    if args['login']:
        user = args["--user"] if "--user" in args else ""
        password = args["--password"] if "--password" in args else ""
        login(host=args["-H"], user=user, password=password)
    elif args['logout']:
        logout()
    elif args['transfer']:
        if args['--config']:
            transfer_config(config_name=args['--config'])
    elif args['query']:
        qg = QueryGui()
        job_id = args['--job_id']
        start_date = args['--start_date']
        end_date = args['--end_date']
        batch_job_only = args['--batch_job_only']
        measurement_only = args['--measurement_only']
        all_jobs = bool(args['--all'])
        list_job_ids = bool(args['--list_job_ids'])
        experiment_file = args['--experiment_file']
        qg.get_data(job_id=job_id, end_date=end_date, start_date=start_date,
                    influx_only=bool(measurement_only), cdb_only=bool(batch_job_only), all=all_jobs,
                    list_job_ids=list_job_ids, experiment_file=experiment_file)
    elif args['monitor']:
        qg = QueryGui()
        job_id = args['--job_id']
        delta_t = args['--delta_t']
        file_to_dump_times = args['--experiment_file']
        monitor_direct = bool(args['--monitor_direct'])
        if monitor_direct:
            transfer_url = os.getenv('TRANSFER_SERVICE_URL')
            if transfer_url is None:
                print("Please set the env variable TRANSFER_SERVICE_URL of the transfer-service")
            else:
                print("Directly monitoring job on: ", transfer_url)
                qg.monitor_direct(job_id, int(timeparse(delta_t)), file_to_dump_times)
        else:
            qg.monitor(job_id, int(timeparse(delta_t)), file_to_dump_times)
