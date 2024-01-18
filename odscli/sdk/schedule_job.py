import click
import odscli.sdk.token_utils as token_utils
import requests
import odscli.sdk.constants as constants
import json
from datetime import datetime


@click.group('schedule_cli')
@click.pass_context
def schedule_cli():
    pass


@schedule_cli.group('schedule')
def schedule():
    pass


@schedule.command('ls')
def ls():
    host, user, token = token_utils.readConfig()
    url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/list"
    cookies = dict(ATOKEN=token)
    resp = requests.get(url, params={'userEmail': user}, cookies=cookies)
    print(resp.status_code)
    print(resp.text)


@schedule.command('details')
@click.argument('job_uuid', type=click.UUID)
def details(job_uuid):
    host, user, token = token_utils.readConfig()
    url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/details"
    cookies = dict(ATOKEN=token)
    resp = requests.get(url, params={'jobUuid': job_uuid}, cookies=cookies)
    print(resp.status_code)
    print(resp.text)


@schedule.command('rm')
@click.argument('job_uuid', type=click.UUID)
def rm(job_uuid):
    host, user, token = token_utils.readConfig()
    url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/details"
    cookies = dict(ATOKEN=token)
    resp = requests.delete(url, params={'jobUuid': job_uuid}, cookies=cookies)
    print(resp.status_code)
    print(resp.text)


@schedule.command('submit')
@click.argument('source_credential_id', type=click.STRING)
@click.argument('source_type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.option('--file_source_path', '-fsp', default='/', show_default=True, type=click.Path())
@click.option('--files', '-f', multiple=True, prompt='Enter your files or folders you with to transfers.')
@click.argument('destination_credential_id', type=click.STRING)
@click.argument('destination_type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.option('--file_destination_path', '-fdp', default='/', show_default=True, type=click.Path())
@click.option("--compress", '-c', is_flag=True, default=False)
@click.option('--encrypt', '-e', is_flag=True, default=False)
@click.option('--optimizer', '-o', type=click.Choice(['BO', 'SGD', 'DDPG', 'PPO', ""]), default="")
@click.option('--overwrite', is_flag=True, default=False)
@click.option('--retry', type=click.INT, default=5)
@click.option('--verify', '-v', is_flag=True, default=False)
@click.option('--cc', type=click.IntRange(1, 64), help='the number of concurrent files to transfer', default=4)
@click.option('--p', type=click.IntRange(0, 64), help='the number of parallel threads to use per concurrent file',
              default=1)
@click.option('--pp', type=click.IntRange(1, 100),
              help='The number of reads to one write operation. Also referred to as pipelining', default=10)
@click.option('--chunk_size', '-cs', type=click.IntRange(1000000, 2000000000), help="Number of bytes per chunk",
              default='10000000')
@click.option('--schedule_time', type=click.DateTime(), default=datetime.now(),
              help='ISO 8061 date time string on when to run the job.')
@click.option('--transfer_node_name', '--node', type=click.STRING, default="")
@click.option('--save_to_config', is_flag=True, default=False)
def submit(source_credential_id, source_type, file_source_path, files, destination_credential_id, destination_type,
           file_destination_path, compress, encrypt, optimizer, overwrite, retry, verify, cc, p, pp, chunk_size,
           transfer_node_name, schedule_time, save_to_config):
    host, user, token = token_utils.readConfig()

    body = {
        "ownerId": user,
        "source": {
            "credId": source_credential_id,
            "type": source_type,
            "fileSourcePath": file_source_path
        },
        "destination": {
            "credId": destination_credential_id,
            "type": destination_type,
            "fileDestinationPath": file_destination_path
        },
        "options": {
            "compress": compress,
            "encrypt": encrypt,
            "optimizer": optimizer,
            "overwrite": overwrite,
            "retry": retry,
            "verify": verify,
            "concurrencyThreadCount": cc,
            "parallelThreadCount": p,
            "pipeSize": pp,
            "chunkSize": chunk_size,
            "scheduledTime": schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        },
        "transferNodeName": transfer_node_name
    }

    resourceList = []
    for file in files:
        resourceList.append({"path": file, "id": file, "size": 0})
    body['source']['resourceList'] = resourceList
    # url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/schedule"
    if save_to_config:
        with open("transfer_" + source_credential_id + "_to_" + destination_credential_id + ".json", "w+") as f:
            json.dump(body, f, indent=4)

    url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/schedule"
    cookies = dict(ATOKEN=token)
    resp = requests.post(url, cookies=cookies, json=body)
    print(resp.status_code)
    print(resp.text)


@schedule.command("config")
@click.argument('filename', type=click.Path(exists=True, writable=True))
@click.option('--schedule_time', type=click.DateTime(), default=datetime.now(),
              help='ISO 8061 date time string on when to run the job.')
@click.option('--schedule_direct', type=click.STRING, default="")
def config(filename, schedule_time, schedule_direct):
    try:
        with open(filename, "r") as json_file:
            data = json.load(json_file)
            data['options']['scheduledTime'] = schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            print(data)
            if len(schedule_direct) > 1:
                url = 'http://'+schedule_direct+'/job/direct'
                resp = requests.post(url, json=data)
                print(resp.status_code)
                print(resp.text)
            else:
                host, user, token = token_utils.readConfig()
                url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/schedule"
                cookies = dict(ATOKEN=token)
                resp = requests.post(url, cookies=cookies, json=data)
                print(resp.status_code)
                print(resp.text)
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


@schedule.command("parameters")
@click.argument('node_name', type=click.STRING)
@click.option('--concurrency','-cc', type=click.INT, help="Number of files to transfer concurrently")
@click.option('--parallelism', '-p', type=click.INT, help="Number of parallel threads per file")
@click.option('--pipelining', '-pp', type=click.INT, help="Pipelining level to use for file transfer")
@click.option('--chunksize', '-cs', type=click.INT, help="Chunksize to use for file transfer, currently not supported")
def parameters(node_name, concurrency, parallelism, pipelining, chunksize):
    body = {
        "concurrency": concurrency,
        "parallelism": parallelism,
        "pipelining": pipelining,
        "chunkSize": chunksize,
        "transferNodeName": node_name
    }
    host, user, token = token_utils.readConfig()

    url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/adjust"
    cookies = dict(ATOKEN=token)
    resp = requests.put(url, cookies=cookies, json=body)
    print(resp.status_code)
    print(resp.text)
