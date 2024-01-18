import click
from rich.table import Table
from rich.console import Console
import odscli.sdk.token_utils as token_utils
import odscli.sdk.constants as constants
import requests

console = Console()


@click.group('endpoint_cli')
@click.pass_context
def endpoint_cli():
    pass


@endpoint_cli.group('management')
def management():
    pass


@management.command('ls')
@click.argument('credentialid')
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.option('--path', default="/", help="For sftp, scp, ftp, http please enter the path you with to enter")
@click.option('--id', default="", help="For gdrive, box, dropbox please pass in the ID of the folder")
def ls(credentialid, path, type, id):
    host, user, token = token_utils.readConfig()
    req = constants.ODS_PROTOCOL + host + constants.LISTV2
    reqForm = req.format(type=type)
    cookies = dict(ATOKEN=token)
    body = {'credId': credentialid, 'path': path, 'identifier': id}
    res = requests.get(reqForm, params=body, cookies=cookies)  # Needs to be handled better for errors
    file_table = Table(title="Files")
    file_table.add_column("Path")
    file_table.add_column("Name")
    file_table.add_column("Size in Bytes")
    for entry in res.json()['files']:
        file_table.add_row(entry['id'], entry['name'], str(entry['size']))
    console.print(file_table)


@management.command("rm")
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.argument("credentialid", type=click.STRING)
@click.argument("path_to_delete", type=click.STRING)
def rm(type, credentialid, path_to_delete):
    host, user, token = token_utils.readConfig()
    req = constants.ODS_PROTOCOL + host + constants.REMOVEV2
    reqForm = req.format(type=type)
    print(reqForm)
    cookies = dict(ATOKEN=token)
    body = {'credId': credentialid, 'toDelete': path_to_delete, "id": "", "path": ""}
    res = requests.post(reqForm, json=body, cookies=cookies)  # Needs to be handled better for errors
    print(res.status_code)


@management.command('mkdir')
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.argument("credentialid", type=click.STRING)
@click.argument('folder_to_create', type=click.STRING)
@click.option('--path', default="", help="For sftp, scp, ftp, http please enter the path you with to enter")
@click.option('--id', default="", help="For gdrive, box, dropbox please pass in the ID of the folder")
def mkdir(type, credentialid, folder_to_create, path, id):
    host, user, token = token_utils.readConfig()
    req = constants.ODS_PROTOCOL + host + constants.MKDIRV2
    reqForm = req.format(type=type)
    cookies = dict(ATOKEN=token)
    body = {'credId': credentialid, 'path': path, 'id': id, 'folderToCreate': folder_to_create}
    res = requests.post(reqForm, json=body, cookies=cookies)  # Needs to be handled better for errors
    print(res.status_code)
    print(res.text)
