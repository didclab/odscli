import click
from odscli.sdk.schedule_job import schedule_cli
from odscli.sdk.credential import credential_cli
from odscli.sdk.endpoint_management import endpoint_cli
from odscli.sdk.query_transfer_data import query_cli
from odscli.sdk.login import auth_cli
from odscli.sdk.carbon_measure import measure_cli

odscli = click.CommandCollection(sources=[schedule_cli, credential_cli, endpoint_cli, query_cli, auth_cli, measure_cli])

if __name__ == '__main__':
    odscli()
