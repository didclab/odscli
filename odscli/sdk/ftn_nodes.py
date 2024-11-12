import click
import requests
from rich.console import Console
from rich.table import Table
from rich import print

from odscli.sdk import token_utils, constants

console = Console()


@click.group('nodes_cli')
@click.pass_context
def nodes_cli():
    pass


@nodes_cli.group('nodes')
def nodes():
    pass


@nodes.command("ls")
@click.argument('type', type=click.Choice(['ods', 'connectors']))
def ls_connectors(type):
    host, user, token = token_utils.readConfig()
    if type == 'connectors':
        req = constants.ODS_PROTOCOL + host + constants.NODE_LIST_CONNECTORS
        req = req.format(user=user)
        node_table_name = "{user} ODS Connectors".format(user=user)
    else:
        req = constants.ODS_PROTOCOL + host + constants.NODE_LIST_ODS
        node_table_name = "ODS File Transfer Nodes"

    cookies = dict(ATOKEN=token)
    res = requests.get(req, cookies=cookies)
    node_table = build_node_table(node_table_name)
    for entry in res.json():
        odsOwner = entry['odsOwner']
        nodeName = entry['nodeName']
        nodeUuid = entry['nodeUuid']
        runningJob = entry['runningJob']
        online = entry['online']
        jobId = entry['jobId']
        jobUuid = entry['jobUuid']
        node_table.add_row(odsOwner, nodeName, nodeUuid, str(runningJob), str(online), str(jobId), jobUuid)

    console.print(node_table)


@nodes.command("count")
def ls_node_count():
    host, user, token = token_utils.readConfig()
    req = constants.ODS_PROTOCOL + host + constants.NODE_COUNT
    cookies = dict(ATOKEN=token)
    res = requests.get(req, cookies=cookies)
    print(res.json())


def build_node_table(name):
    node_table = Table(title=name)
    node_table.add_column("ODS Owner")
    node_table.add_column("Node Name")
    node_table.add_column("Node UUID")
    node_table.add_column("Running Job")
    node_table.add_column("Online")
    node_table.add_column("Job Id")
    node_table.add_column("Job UUID")
    return node_table
