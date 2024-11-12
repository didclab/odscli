import json
from datetime import datetime
from inspect import trace

from rich.columns import Columns
from rich.panel import Panel

from odscli.sdk import token_utils
import odscli.sdk.constants as constants
import requests
import click
from rich.console import Console
import odscli.sdk.carbon_scheduler_gui as scheduler_gui

console = Console()


@click.group('carbon_cli')
@click.pass_context
def carbon_cli():
    pass


@carbon_cli.group('carbon')
def carbon():
    pass


@carbon.command('entries', help="List the measurements for a job measured on a given node")
@click.argument('job_uuid', type=click.UUID)
@click.argument('transfer_node_name', type=click.STRING)
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def queryCarbonEntries(job_uuid, transfer_node_name, save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_NODE_AND_JOB.format(
        transferNodeName=transfer_node_name, jobUuid=job_uuid)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    data = send_request(uri=uri, cookies=cookies, headers=headers, params={})
    if data is None: return

    if save_to_file:
        save_data_to_file(data, save_to_file)
    scheduler_gui.buildMainCarbonTable(data, console)


@carbon.command('user', help="List carbon measurements for a user across all jobs and nodes")
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def getCarbonEntriesForUser(save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_USER
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}

    data = send_request(uri, cookies, headers, {})
    if data is None: return

    if save_to_file:
        save_data_to_file(data, save_to_file)

    data_sorted = sorted(data, key=lambda job: datetime.fromisoformat(job["timeMeasuredAt"]))
    scheduler_gui.buildMainCarbonTable(data_sorted, console)


@carbon.command("job", help="List all carbon measurements for a job")
@click.argument('job_uuid', type=click.UUID)
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def job_measurements(job_uuid, save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_JOB.format(jobUuid=job_uuid)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    data = send_request(uri, cookies, headers, params={})
    print(data)
    if data is None: return
    if save_to_file: save_data_to_file(data, save_to_file)

    scheduler_gui.buildMainCarbonTable(data, console)


@carbon.command("latest", help="Get latest carbon measurement for scheduled job")
@click.argument('job_uuid', type=click.UUID)
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def query_latest_job_measurement(job_uuid, save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_LATEST.format(jobUuid=job_uuid)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    data = send_request(uri, cookies, headers, params={})
    if data is None: return
    if save_to_file: save_data_to_file(data, save_to_file)

    trace_route_table = scheduler_gui.buildTraceRouteTable(data['transferNodeName'], data['jobUuid'],
                                                           data['timeMeasuredAt'], data['traceRouteCarbon'])
    console.print(trace_route_table)


@carbon.command("node", help="Get the carbon measurements produced by a Node")
@click.argument('transfer_node_name', type=click.STRING)
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def query_measurements_made_by_node(transfer_node_name, save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_NODE.format(
        transferNodeName=transfer_node_name)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    data = send_request(uri, cookies, headers, params={})
    if data is None: return
    if save_to_file: save_data_to_file(data, save_to_file)

    scheduler_gui.buildMainCarbonTable(data, console)


@carbon.command("result",
                help="The initial and final measurement for a scheduled job. Allows to compare the carbon intensity of the job that caused it to launch")
@click.argument('job_uuid', type=click.UUID)
@click.option('--save_to_file', type=click.Path(), default=None, help="File path to save the output. Format is in json")
def query_result(job_uuid, save_to_file):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CARBON_API + constants.CARBON_RESULT.format(job_uuid=job_uuid)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    data = send_request(uri, cookies, headers, params={})
    if data is None: return
    if save_to_file: save_data_to_file(data, save_to_file)
    start_json = data['start']
    end_json = data['end']
    start_table = scheduler_gui.buildTraceRouteTable(transferNodeName=start_json['transferNodeName'],
                                                     jobUuid=start_json['jobUuid'],
                                                     timeMeasuredAt=start_json['timeMeasuredAt'],
                                                     trace_route_data=start_json['traceRouteCarbon'])
    end_table = scheduler_gui.buildTraceRouteTable(transferNodeName=end_json['transferNodeName'],
                                                   jobUuid=end_json['jobUuid'],
                                                   timeMeasuredAt=end_json['timeMeasuredAt'],
                                                   trace_route_data=end_json['traceRouteCarbon'])
    columns = Columns([Panel(start_table, title="Initial Job Measurement"),
                       Panel(end_table, title="Last Job Measurement Before Job Execution")])
    console.print(columns)


def send_request(uri, cookies, headers, params):
    try:
        console.print(f"Sending request: {uri}")
        resp = requests.get(uri, cookies=cookies, headers=headers, params=params)
        return resp.json()
    except requests.RequestException as e:
        console.print(f"[red]Error fetching data: {e.errno} ")
        return None


def save_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
    console.print(f"[green]Data saved to {file_path}[/green]")
