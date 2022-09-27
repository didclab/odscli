import os
import requests
import configparser
import sdk.constants as constants
#Adds the hostname, username, password and user token for the ACTIVE onedatashare backend
# odsConfig.ini
#Python ConfigParser

config_path=os.environ['HOME']+"/.config/"
config_file_name = ".odsConfig.ini"
config_absolute_path = config_path + config_file_name
def writeConfig(hostname,username,token):
    config = configparser.ConfigParser()
    config["OneDataShare"] = {'hostname':hostname,'username':username,'token':token}
    os.makedirs(config_path, exist_ok=True)
    with open(config_absolute_path, 'w') as configfile:
        try:
            config.write(configfile)
        except:
            print("Error Writing Config")
#Attempts to read onedatashare backend information from config file
#Throws Exception when there is an issue reading config or it does not exist
#Returns Hostname, Username, Token
#Python ConfigParser

def readConfig():
    config = configparser.ConfigParser()
    try:
        config.read(config_absolute_path)
    except:
        print('Config Read Issue are you logged in?')
        return False
    return config['OneDataShare']['hostname'],config['OneDataShare']['username'],config['OneDataShare']['token']


def isValidUser(host:str,email:str)->bool:
    isValidURL = "http://"+host+constants.VALIDATE_EMAILV2
    body = {'email':email}
    req = requests.post(isValidURL,json=body)# Needs to be handled better for errors
    return req.json()


def login(host,user,password):
    if isValidUser(host,user):
        loginURL = "https://"+host+constants.AUTHENTICATEV2
        body = {'email':user,'password':password}
        req = requests.post(loginURL,json=body, timeout=10)
        atoken = req.cookies.get_dict()# Needs to be handled better for errors
        if req.status_code != 200:
            print("\nError Handling Login\n")
            if req.status_code == 401:
                print("Possibly Bad Password")
            return False,""
        print("\nUser Authentication Token:")# Move this TO THE CLI SIDE
        print(atoken['ATOKEN'])# Move this TO THE CLI SIDE
        if req.status_code==200:
            writeConfig(host,user,atoken.get('ATOKEN'))
            return True,atoken.get('ATOKEN')
    else:
        print("Not Valid User")
        return False,""
def logout():
    writeConfig('None','None','None')