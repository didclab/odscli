import click
import odscli.sdk.constants as constants
import odscli.sdk.token_utils as token_utils
import requests
from rich.console import Console
from rich.table import Table

console = Console()
@click.group('credential_cli')
@click.pass_context
def credential_cli():
    pass


@credential_cli.group('credential')
def credential():
    pass


@credential.command('ls')
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))

def ls_credential(type):
    host, user, token = token_utils.readConfig()
    uri = constants.ODS_PROTOCOL + host + constants.CRED_ACCOUNT_REGISTERV2
    req_formated = uri.format(type=type)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    req = requests.get(req_formated, headers=headers, cookies=cookies)  # Needs to be handled better for errors
    credential_table = Table(title="Credentials")
    credential_table.add_column('Credential Ids')
    credential_list = req.json()['list']
    for element in credential_list:
        credential_table.add_row(element)
    console.print(credential_table)

@credential.command('rm')
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.argument('credentialid', type=click.STRING)
def rm_credential(type, credentialid):
    host, user, token = token_utils.readConfig()
    req = constants.ODS_PROTOCOL + host + constants.CRED_ACCOUNT_DELETE
    reqFormated = req.format(type=type, credID=credentialid)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    req = requests.delete(reqFormated, headers=headers, cookies=cookies)  # Needs to be handled better for errors
    if 199 < req.status_code < 300:
        print("Credential with Id deleted: " + credentialid)

@credential.command('add')
@click.argument('uri', default="", type=click.STRING)
@click.argument('type',
                type=click.Choice(['dropbox', 'gdrive', 'sftp', 'ftp', 'box', 's3', 'gftp', 'http', 'vfs', 'scp']))
@click.option('--username', default="", type=click.STRING)
@click.option('--password', prompt=False, hide_input=False, confirmation_prompt=False, default=None)
@click.option('--credentialid', type=click.STRING, default=None)
@click.option('--keyfile', type=click.Path(exists=True), default=None)
def add_credential(uri, username, password, credentialid, keyfile, type):
    host, user, token = token_utils.readConfig()
    ods_uri = constants.ODS_PROTOCOL + host + constants.CRED_ACCOUNT_REGISTERV2
    req_formated = ods_uri.format(type=type)
    cookies = dict(ATOKEN=token)
    headers = {"Authorization": "Bearer " + token + ""}
    body = {
        "uri": uri,
        "username": username,
        "accountId": credentialid
    }
    if keyfile:
        with open(keyfile, 'rb') as keyfile_data:
            body['secret'] = keyfile_data.read()
    elif password:
        body['secret'] = password

    req = requests.post(req_formated, headers=headers, cookies=cookies, json=body)
    if 199 < req.status_code < 300:
        print("Credential with id {} has been added".format(credentialid))
    print(req.status_code)
    print(req.text)
