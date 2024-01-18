import time

import click
import pandas as pd

from rich.progress import Progress, TextColumn, BarColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.progress import DownloadColumn
from rich.console import Console
from rich.table import Table
from odscli.sdk.meta_query_gui import QueryGui, MetaQueryAPI
import json
from datetime import datetime
from math import ceil

BASEPATH = "/api/metadata"
JOB = "/job"
JOB_DIRECT = "/api/v1/job"
ALL = "/all"
JOB_IDS = "/jobids"
JOBS = "/jobs"
MEASUREMENT = "/measurement"
MEASUREMENTS = "/measurements"
USER = "/user"
RANGE = "/range"
MONITOR = "/monitor"

console = Console()


@click.group('query_cli')
@click.pass_context
def query_cli():
    pass


@query_cli.group('query')
def query():
    pass



@query.command("uuids")
def list_user_job_uuids():
    meta_query_api = MetaQueryAPI()
    job_uuid_table = Table()
    job_uuids = meta_query_api.query_job_uuids()
    job_uuid_table.add_column("Job UUIDS")
    for id in job_uuids:
        job_uuid_table.add_row(str(id))
    console.print(job_uuid_table)


@query.command("progress")
@click.argument("job_uuid", type=click.UUID)
@click.option("--retry", "-r", type=click.INT, default=30)
def progress(job_uuid, retry):
    meta_query_api = MetaQueryAPI()
    # transfer_summary = meta_query_api.query_job_progress(job_uuid)
    # print(transfer_summary)
    max_no_progress_checks = retry
    retry_progress = 0
    prev_transfer_summary = None

    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    task = progress.add_task("[cyan]Transferring...", total=None, start=False)
    while not progress.finished:
        transfer_summary = meta_query_api.query_job_progress(job_uuid)
        if prev_transfer_summary is not None:
            if transfer_summary['bytesRead'] == prev_transfer_summary['bytesRead'] and transfer_summary[
                'bytesWritten'] == prev_transfer_summary['bytesWritten']:
                retry_progress += 1
            else:
                progress.update(task, completed=float(transfer_summary['progressPercentage']))
                progress.refresh()
                retry_progress = 0

        if retry_progress == max_no_progress_checks:
            progress.stop()
            console.print("[yellow] \nNo progress for too long. Exiting progress monitoring.")
            return

        prev_transfer_summary = transfer_summary
        time.sleep(1)


@query.command("monitor")
@click.option("--job_id", type=click.INT)
@click.option("--url", "-u", type=click.STRING, help="url to query if using an ods connector", default=None)
@click.option("--experiment_file", type=click.Path(writable=True, dir_okay=False),
              help="The file to put the results into")
@click.option("--delta", type=click.INT, default=1)
@click.option("--retry", type=click.INT, default=5)
def monitor_job(job_id, url, experiment_file, delta, retry):
    local_retry = 0
    meta_query_api = MetaQueryAPI()
    pq = QueryGui()
    if job_id is None:
        if url is not None:
            job_ids = meta_query_api.query_job_ids_direct(transfer_url=url)
        else:
            job_ids = meta_query_api.query_all_jobs_ids()
        job_id = job_ids[-1]
    print("Using job_id: ", job_id)
    done_map = {}
    with Progress() as progress:
        if url is not None:
            job_batch_cdb = meta_query_api.query_transferservice_direct(job_id, url)
        else:
            job_batch_cdb = meta_query_api.query_job_id_cdb(job_id)
        visual_job_cdb = wrap_json_cdb_to_have_defaults(job_batch_cdb)
        console.print(visualize_job_table(visual_job_cdb))
        file_progress_id_map = {}
        file_last_write_count_map = {}

        while local_retry < retry:
            if url is not None:
                job_batch_cdb = meta_query_api.query_transferservice_direct(job_id, url)
            else:
                job_batch_cdb = meta_query_api.query_job_id_cdb(job_id)

            job_batch_cdb = wrap_json_cdb_to_have_defaults(job_batch_cdb)
            for step in job_batch_cdb['batchSteps']:
                entityInfo = json.loads(
                    job_batch_cdb['jobParameters'][step['step_name']])  # json format of file in jobParams
                if step['step_name'] not in file_progress_id_map:
                    file_size = entityInfo['size']
                    chunk_size = entityInfo['chunkSize']
                    total_chunks = ceil(file_size / chunk_size)
                    file_task = progress.add_task("[green]Processing: "+step['step_name'], total=total_chunks)
                    progress.update(file_task, advance=int(step['writeCount']))
                    file_progress_id_map[step['step_name']] = file_task
                    file_last_write_count_map[step['step_name']] = int(step['writeCount'])
                    if step['status'] == ["COMPLETED", "FAILED", "ABANDONED", "STOPPED"]:
                        progress.update(file_task_id, completed=True)
                        progress.remove_task(file_task_id)
                        console.print()
                else:
                    file_task_id = file_progress_id_map[step['step_name']]
                    written = step['writeCount'] - file_last_write_count_map[step['step_name']]
                    file_last_write_count_map[step['step_name']] = step['writeCount']
                    progress.update(file_task_id, advance=written)
                    if step['status'] in ["COMPLETED", "FAILED", "ABANDONED", "STOPPED"]:
                        progress.update(file_task_id, description="[blue]Completed File: " + step['step_name'])
                if step['status'] in ["COMPLETED", "FAILED", "ABANDONED", "STOPPED"]:
                    if step['step_name'] not in done_map:
                        print('File: ', step['step_name'])
                        file_size_mbps = (entityInfo['size'] / 1000000) * 8
                        print('\tFile size in Megabits: ', file_size_mbps)
                        file_time_seconds = pd.Timedelta(pd.to_datetime(step['endTime']) - pd.to_datetime(step['startTime'])).seconds
                        file_time_seconds = max(file_time_seconds, 1)
                        print('\tTotal Time for file to complete: ', file_time_seconds)
                        print('\tTotal File throughput: ', file_size_mbps / file_time_seconds, "Mbps \n")
                        # progress.update(file_progress_id_map[step['step_name']], completed=step['writeCount'])
                        done_map[step['step_name']] = True

            progress.refresh()
            if job_batch_cdb['status'] in ["COMPLETED", "FAILED", "ABANDONED", "STOPPED"]:
                pq.finished_job_stdout(batch_job_cdb=job_batch_cdb, output_file=experiment_file, job_id=job_id)
                print('\n JobId: ', job_id, ' has final status of ', job_batch_cdb['status'])
                return
            time.sleep(1)


@query.command("ids")
@click.option("--url", "-u", type=click.STRING,
              help="the url of the transfer-service to query if you want to query your ODS Connector")
def list_user_job_ids(url):
    meta_query_api = MetaQueryAPI()
    if url is not None:
        job_ids = meta_query_api.query_job_ids_direct(url)
    else:
        job_ids = meta_query_api.query_all_jobs_ids()
    job_id_table = Table()
    job_id_table.add_column("Job Ids")
    for id in job_ids:
        job_id_table.add_row(str(id))
    console.print(job_id_table)


@query.command("job")
@click.argument("id")
@click.option("--url", "-u", type=click.STRING,
              help="The url of the transfer-service to query if you want to query your ODS Connector")
def query_job(id, url):
    meta_query_api = MetaQueryAPI()
    if url is not None:
        json_cdb = meta_query_api.query_transferservice_direct(id, url)
    else:
        json_cdb = meta_query_api.query_job_id_cdb(id)

    json_cdb = wrap_json_cdb_to_have_defaults(json_cdb)
    job_param_column = visualize_job_param_column(json_cdb['jobParameters'])
    job_table = visualize_job_table(json_cdb)
    step_table = visualize_step_table(json_cdb)
    console.print(job_table)
    console.print(job_param_column)
    console.print(step_table)


# Problem:
# 1. We need to make the querying more accurate since multiple buckets can have the same jobId.
# Consider ODS Connector using HSQL and ODS prod same user having multiple job id=1. Need to clean that out.
# Show the slowest throughput of start read -> write end.
# Add an API call to allow the user query progress of the job without them needing the whole influx json.
@query.command("measurements")
@click.argument("id")
@click.option("network", "-n", is_flag=True, default=False)
@click.option("host", "-h", is_flag=True, default=False, help="Show host properties such as: (Memory, CPU count)")
@click.option("save_to_file", '-stf', type=click.Path(), help="Default")
def query_job_measurements(id, network, host, save_to_file):
    meta_query_api = MetaQueryAPI()
    influx_json = meta_query_api.query_job_id_influx(id)
    if save_to_file:
        with open(save_to_file, 'w') as json_file:
            json.dump(influx_json, json_file)
    print(influx_json)
    visualize_influx_data(influx_json, network, host)


@query.command("measurement_range")
@click.option('--start', type=click.DateTime(), default=datetime.now(),
              help="ISO 8061 string of starting date time point")
@click.option('--end', type=click.DateTime(), default=datetime.now(), help="ISO 8061 string of ending date time point")
@click.option("--save_to_file", type=click.Path(exists=True, writable=True))
def measurement_range(start, end, save_to_file):
    meta_query_api = MetaQueryAPI()
    influx_points = meta_query_api.query_range_influx(start, end)
    visualize_influx_data(influx_points, True, True)


@query.command("job_range")
@click.option('--start', type=click.DateTime(), default=datetime.now(),
              help="ISO 8061 string of starting date time point")
@click.option('--end', type=click.DateTime(), default=datetime.now(), help="ISO 8061 string of ending date time point")
@click.option("--save_to_file", type=click.Path(exists=False, writable=True))
def query_cdb(start, end, save_to_file):
    print(start)
    print(end)
    meta_query_api = MetaQueryAPI()

    cdb_data = meta_query_api.query_range_cdb(start, end)
    print(cdb_data)


def visualize_influx_data(influx_json, network_flag, host_flag):
    job_table = Table(title="Transfer Measurement")
    job_table.add_column("ODS User")
    job_table.add_column("Transfer Node Name")
    job_table.add_column("Job Id")
    job_table.add_column("Job Size (Bytes)")
    job_table.add_column("Average File Size (Bytes)")
    job_table.add_column("Source Type")
    job_table.add_column("Source Credential Id")
    job_table.add_column("Read Throughput")
    job_table.add_column("Destination Type")
    job_table.add_column("Destination Credential Id")
    job_table.add_column("Write Throughput")
    job_table.add_column("Concurrency")
    job_table.add_column("Parallelism")
    job_table.add_column("Pipelining")

    if network_flag:
        network_table = Table(title="Network Table")
        network_table.add_column("Source Latency")
        network_table.add_column("Source RTT")
        network_table.add_column("Bytes Read")
        network_table.add_column("Destination Latency")
        network_table.add_column("Destination RTT")
        network_table.add_column("Bytes Written")

    if host_flag:
        host_table = Table(title="Host Table")
        host_table.add_column("Memory (Bytes)")
        host_table.add_column("Max Memory (Bytes)")
        host_table.add_column("Free Memory (Bytes)")
        host_table.add_column("Allocated Memory (Bytes)")
        host_table.add_column("Core Count")
        host_table.add_column("Cpu Frequency")

    for entry in influx_json:
        if network_flag:
            network_table.add_row(str(entry['sourceLatency']), str(entry['sourceRtt']), str(entry['bytesRead']),
                                  str(entry['destLatency']),
                                  str(entry['destinationRtt']),
                                  str(entry['bytesWritten']))

        if host_flag:
            host_table.add_row(str(entry['memory']), str(entry['maxMemory']),
                               str(entry['freeMemory']), str(entry['allocatedMemory']), str(entry['coreCount']))

        job_table.add_row(entry['odsUser'], entry['transferNodeName'], str(entry['jobId']), str(entry['jobSize']),
                          str(entry['avgFileSize']), entry['sourceType'], entry['sourceCredId'],
                          str(entry['readThroughput']), entry['destType'], entry['destCredId'],
                          str(entry['writeThroughput']), str(entry['concurrency']), str(entry['parallelism']),
                          str(entry['pipelining']))
    console.print(job_table)
    if network_flag:
        console.print(network_table)
    if host_flag:
        console.print(host_table)


def visualize_step_table(job_json):
    step_table = Table(title="File Table")
    step_table.add_column("File Name")
    step_table.add_column("Size (Bytes)")
    step_table.add_column("Chunk Size")
    step_table.add_column("start time")
    step_table.add_column("end time")
    step_table.add_column("readCount")
    step_table.add_column("writeCount")
    step_table.add_column("status")

    for step in job_json['batchSteps']:
        entityInfo = json.loads(job_json['jobParameters'][step['step_name']])
        file_id = entityInfo['id']
        path = entityInfo['path']
        size = entityInfo['size']
        chunkSize = entityInfo['chunkSize']

        step_table.add_row(step['step_name'], str(size), str(chunkSize), step['startTime'], step['endTime'],
                           str(step['readCount']), str(step['writeCount']), step['status'])

    return step_table


def visualize_job_table(job_json):
    job_table = Table(title="Job Table")
    job_table.add_column("Job Id")
    job_table.add_column("Start Time")
    job_table.add_column("End Time")
    job_table.add_column("Job Status")
    job_table.add_column("Exit Code")
    job_table.add_column("Average File Size (Bytes)")
    job_table.add_column("Source Type")
    job_table.add_column("Destination Type")

    job_table.add_row(str(job_json['id']), str(job_json['startTime']), str(job_json['endTime']), job_json['status'],
                      str(job_json['exitCode']),
                      str(job_json['jobParameters']['fileSizeAvg']), job_json['jobParameters']['sourceCredentialType'],
                      job_json['jobParameters']['destCredentialType'])
    return job_table


def visualize_job_param_column(job_param_json):
    # print(job_param_json)
    job_param_table = Table(title="Job Parameters")
    job_param_table.add_column("Name")
    job_param_table.add_column("Value")
    job_param_table.add_row("User Email", job_param_json['ownerId'])
    job_param_table.add_row("Destination Credential Id", job_param_json['destCredential'])
    job_param_table.add_row("Compress", str(job_param_json['compress']))
    job_param_table.add_row("Initial Concurrency", str(job_param_json['concurrency']))
    job_param_table.add_row("Initial Parallelism", str(job_param_json['parallelism']))
    job_param_table.add_row("Initial Pipelining", str(job_param_json['pipelining']))
    job_param_table.add_row("File Count", job_param_json['fileCount'])
    job_param_table.add_row("File Size Average", job_param_json['fileSizeAvg'])
    job_param_table.add_row("Retry", str(job_param_json['retry']))
    job_param_table.add_row("Source Credential Id", job_param_json['sourceCredential'])
    # job_param_table.add_row("Source Uri", job_param_json['sourceURI'])
    job_param_table.add_row("Source Base Path", job_param_json['sourceBasePath'])
    job_param_table.add_row("Destination Credential Id", job_param_json['destCredential'])
    job_param_table.add_row("Destination Base Path", job_param_json['destBasePath'])
    return job_param_table


def wrap_json_cdb_to_have_defaults(cdb_json):
    if "startTime" not in cdb_json:
        cdb_json['startTime'] = ""
    if "endTime" not in cdb_json:
        cdb_json['endTime'] = ""
    for step in cdb_json['batchSteps']:
        if "startTime" not in step:
            step['startTime'] = ""
        if "endTime" not in step:
            step['endTime'] = ""
    return cdb_json
