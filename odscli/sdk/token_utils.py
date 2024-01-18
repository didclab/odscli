import os
import requests
import configparser
import odscli.sdk.constants as constants

# Adds the hostname, username, password and user token for the ACTIVE onedatashare backend
# odsConfig.ini
# Python ConfigParser

config_path = os.environ['HOME'] + "/.config/"
config_file_name = ".odsConfig.ini"
config_absolute_path = config_path + config_file_name

config_transfer_file = ".odsConfigTransfer_"
config_transfer_absolute_path = config_path + config_transfer_file


def writeConfig(hostname, username, token):
    config = configparser.ConfigParser()
    config["OneDataShare"] = {'hostname': hostname, 'username': username, 'token': token}
    os.makedirs(config_path, exist_ok=True)
    with open(config_absolute_path, 'w') as configfile:
        try:
            config.write(configfile)
        except:
            print("Error Writing Config")


# Attempts to read onedatashare backend information from config file
# Throws Exception when there is an issue reading config or it does not exist
# Returns Hostname, Username, Token
# Python ConfigParser

def readConfig():
    config = configparser.ConfigParser()
    try:
        config.read(config_absolute_path)
    except:
        print('Config Read Issue are you logged in?')
        return False
    return config['OneDataShare']['hostname'], config['OneDataShare']['username'], config['OneDataShare']['token']


def isValidUser(host: str, email: str) -> bool:
    isValidURL = "http://" + host + constants.VALIDATE_EMAILV2
    body = {'email': email}
    req = requests.post(isValidURL, json=body)  # Needs to be handled better for errors
    return req.json()


def login(host, user, password):
    if isValidUser(host, user):
        loginURL = "https://" + host + constants.AUTHENTICATEV2
        body = {'email': user, 'password': password}
        req = requests.post(loginURL, json=body, timeout=10)
        atoken = req.cookies.get_dict()  # Needs to be handled better for errors
        if req.status_code != 200:
            print("\nError Handling Login\n")
            if req.status_code == 401:
                print("Possibly Bad Password")
            return False, ""
        print("\nUser Authentication Token:")  # Move this TO THE CLI SIDE
        print(atoken['ATOKEN'])  # Move this TO THE CLI SIDE
        if req.status_code == 200:
            writeConfig(host, user, atoken.get('ATOKEN'))
            return True, atoken.get('ATOKEN')
    else:
        print("Not Valid User")
        return False, ""


def logout():
    writeConfig('None', 'None', 'None')


def writeTransferConfig(username, source_type, source_credid, file_list, dest_type, dest_credid, source_path, dest_path,
                        concurrency, pipesize, parallel, chunksize, compress, encrypt, optimizer, overwrite,
                        retry, verify, save):
    config = configparser.ConfigParser()
    # load existing config
    file_name = config_transfer_absolute_path + username + ".ini"
    if os.path.exists(file_name):
        config.read(file_name)

    # create a new section with transfer_name
    # config["username"] = {"username": username}
    config[save] = {
        "source_type": str(source_type),
        "source_credid": str(source_credid),
        "file_list": file_list,
        "dest_type": str(dest_type),
        "dest_credid": str(dest_credid),
        "source_path": str(source_path),
        "dest_path": str(dest_path),
        "concurrency": str(concurrency),
        "pipesize": str(pipesize),
        "parallel": str(parallel),
        "chunksize": str(chunksize),
        "compress": str(compress),
        "encrypt": str(encrypt),
        "optimizer": str(optimizer),
        "overwrite": str(overwrite),
        "retry": str(retry),
        "verify": str(verify)
    }

    # write back to file
    os.makedirs(config_path, exist_ok=True)
    with open(file_name, 'w') as configfile:
        try:
            config.write(configfile)
        except:
            print("Error Writing Config")


def readTransferConfig(username, transfer_name):
    config = configparser.ConfigParser()
    file_name = config_transfer_absolute_path + username + ".ini"
    if os.path.exists(file_name):
        config.read(file_name)

        # check if the specified transfer_name exists
        if config.has_section(transfer_name):
            transfer_params = config[transfer_name]
            # use split to get a list of files
            file_list = transfer_params.get('file_list', '').split()
            transfer_config = {
                'source_type': transfer_params.get('source_type', ''),
                'source_credid': transfer_params.get('source_credid', ''),
                'file_list': file_list,
                'dest_type': transfer_params.get('dest_type', ''),
                'dest_credid': transfer_params.get('dest_credid', ''),
                'source_path': transfer_params.get('source_path', ''),
                'dest_path': transfer_params.get('dest_path', ''),
                'concurrency': int(transfer_params.get('concurrency', 1)),
                'pipesize': int(transfer_params.get('pipesize', 10)),
                'parallel': int(transfer_params.get('parallel', 0)),
                'chunksize': int(transfer_params.get('chunksize', 10000000)),
                'compress': bool(transfer_params.get('compress', False)),
                'encrypt': bool(transfer_params.get('encrypt', False)),
                'optimizer': transfer_params.get('optimizer', None),
                'overwrite': bool(transfer_params.get('overwrite', False)),
                'retry': int(transfer_params.get('retry', 5)),
                'verify': bool(transfer_params.get('verify', False)),
            }
            return transfer_config
        else:
            print(f"Transfer configuration for {transfer_name} does not exist.")
            return None
    else:
        print("Config file does not exist.")
        return None
