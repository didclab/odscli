import click
from pygments.lexer import default

import odscli.sdk.token_utils as token_utils
import requests
import odscli.sdk.constants as constants
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.pretty import pprint

console = Console()


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
    jobs_data = resp.json()

    # Main table for listing all jobs
    main_table = Table(title="Scheduled Jobs", show_lines=True)
    main_table.add_column("Job #", style="cyan", no_wrap=True)
    main_table.add_column("Job Details", style="magenta")

    # Loop over each job and create a structured table for each
    for index, job_data in enumerate(jobs_data, start=1):
        # Create a detailed table for each job
        job_table = Table.grid(padding=(0, 1))  # Use grid layout to avoid extra column

        # Basic job information table
        basic_info_table = Table(title="Basic Info", show_lines=True)
        basic_info_table.add_column("Field", style="yellow")
        basic_info_table.add_column("Value", style="green")
        basic_info_table.add_row("Owner ID", job_data["ownerId"])
        basic_info_table.add_row("Job UUID", job_data["jobUuid"])
        basic_info_table.add_row("Transfer Node Name", job_data["transferNodeName"])

        # Options table, excluding "chunkSize"
        options_table = Table(title="Options", show_lines=True)
        options_table.add_column("Option", style="cyan")
        options_table.add_column("Value", style="magenta")
        for key, value in job_data["options"].items():
            if key != "chunkSize":  # Exclude chunkSize from visualization
                options_table.add_row(key, str(value))

        # Grid layout for Basic Info and Options side by side
        basic_options_grid = Table.grid()
        basic_options_grid.add_row(basic_info_table, options_table)

        source_table = Table(title="Source Information", show_lines=True)
        source_table.add_column("Field", style="yellow")
        source_table.add_column("Value", style="green")
        source_table.add_row("Type", job_data["source"]["type"])
        source_table.add_row("Credential ID", job_data["source"]["credId"])
        source_table.add_row("Source Path", job_data["source"]["fileSourcePath"])

        file_table = Table(title="File List", show_lines=True)
        file_table.add_column("ID", style="cyan")
        file_table.add_column("Path", style="green")
        file_table.add_column("Size", style="red")
        file_table.add_column("Chunk Size", style="blue")
        for file_info in job_data["source"]["infoList"]:
            file_table.add_row(
                file_info["id"],
                file_info["path"],
                constants.human_readable_size(file_info["size"]),
                constants.human_readable_size(file_info["chunkSize"])
            )
        source_table.add_row("File Information", file_table)

        destination_table = Table(title="Destination Information", show_lines=True)
        destination_table.add_column("Field", style="yellow")
        destination_table.add_column("Value", style="green")
        destination_table.add_row("Type", job_data["destination"]["type"])
        destination_table.add_row("Credential ID", job_data["destination"]["credId"])
        destination_table.add_row("Destination Path", job_data["destination"]["fileDestinationPath"])

        source_dest_grid = Table.grid()
        source_dest_grid.add_row(source_table, destination_table)

        job_table.add_row(basic_options_grid)
        job_table.add_row(source_dest_grid)

        main_table.add_row(f"Job {index}", job_table)

    console.print(main_table)


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
@click.option('--percent_carbon', type=click.FLOAT, default=0.0,
              help="Represents either an increase or a decrease in carbon intensity compared to initial scheduling")
@click.option('--percent_throughput', type=click.FLOAT, default=0.0,
              help="Represents either an increase or a decrease in throughput compared to initial scheduling")
@click.option('--percent_electricity', type=click.FLOAT, default=0.0,
              help="Represents either an increase or a decrease in electricity compared to initial scheduling")
@click.option('--save_to_config', is_flag=True, default=False)
def submit(source_credential_id, source_type, file_source_path, files, destination_credential_id, destination_type,
           file_destination_path, compress, encrypt, optimizer, overwrite, retry, verify, cc, p, pp, chunk_size,
           transfer_node_name, schedule_time, percent_carbon, percent_throughput, percent_electricity, save_to_config):
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
        "transferNodeName": transfer_node_name,
        "transferSla": {
            "percentCarbon": percent_carbon,
            "percentThroughput": percent_throughput,
            "percentElectricity": percent_electricity
        }
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
    console.print("Job Uuid=", resp.text)


@schedule.command("config")
@click.argument('filename', type=click.Path(exists=True, writable=True))
@click.option('--schedule_time', type=click.DateTime(), default=None,
              help='ISO 8061 date time string on when to run the job. Ex: %Y-%m-%dT%H:%M:%S.%fZ')
def config(filename, schedule_time):
    try:
        with open(filename, "r") as json_file:
            data = json.load(json_file)
            if schedule_time is not None:
                data['options']['scheduledTime'] = schedule_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            console.print("Transfer Job Definition sent in:")
            pprint(data)
            host, user, token = token_utils.readConfig()
            url = constants.ODS_PROTOCOL + host + constants.SCHEDULE + "/schedule"
            cookies = dict(ATOKEN=token)
            resp = requests.post(url, cookies=cookies, json=data)
            console.print("Job Uuid=", resp.text)
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


@schedule.command("parameters")
@click.argument('node_name', type=click.STRING)
@click.option('--concurrency', '-cc', type=click.INT, help="Number of files to transfer concurrently")
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
    if resp.status_code < 300 and resp.status_code > 199:
        console.print("Sent in param change request: ")
        pprint(body)
    else:
        console.print(f"[red] Http error number: {resp.status_code}")
