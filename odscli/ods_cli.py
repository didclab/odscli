import click
from odscli.sdk.scheduler import schedule_cli
from odscli.sdk.credential import credential_cli
from odscli.sdk.endpoint_management import endpoint_cli
from odscli.sdk.query_transfer_data import query_cli
from odscli.sdk.login import auth_cli
from odscli.sdk.measure import measure_cli
from odscli.sdk.ftn_nodes import nodes_cli
from odscli.sdk.carbon_scheduler import carbon_cli

odscli = click.CommandCollection(sources=[schedule_cli, credential_cli, endpoint_cli, query_cli, auth_cli, measure_cli, nodes_cli, carbon_cli])

def main():
    odscli()
