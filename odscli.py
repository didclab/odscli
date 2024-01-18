import click
from sdk.schedule_job import schedule_cli
from sdk.credential import credential_cli
from sdk.endpoint_management import endpoint_cli
from sdk.query_transfer_data import query_cli
from sdk.login import auth_cli
from sdk.carbon_measure import measure_cli

odscli = click.CommandCollection(sources=[schedule_cli, credential_cli, endpoint_cli, query_cli, auth_cli, measure_cli])

if __name__ == '__main__':
    odscli()
