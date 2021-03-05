import os
import requests
import configparser
import SDK.constants as constants
#Adds the hostname, username, password and user token for the ACTIVE onedatashare backend
# odsConfig.ini
#Python ConfigParser
def writeConfig(hostname,username,token):
    config = configparser.ConfigParser()
    config["OneDataShare"] = {'hostname':hostname,'username':username,'token':token}
    with open('odsConfig.ini','w') as configfile:
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
        config.read('odsConfig.ini')
    except:
        print('Config Read Issue')
        return False
    return config['OneDataShare']['hostname'],config['OneDataShare']['username'],config['OneDataShare']['token']


def isValidUser(host:str,email:str)->bool:
    isValidURL = "http://"+host+":"+constants.PORT+constants.VALIDATE_EMAILV2
    body = {'email':email}
    req = requests.post(isValidURL,json=body)
    print(req.json())
    return req.json()


def login(host,user,password):
    if isValidUser(host,user):
        loginURL = "http://"+host+":"+constants.PORT+constants.AUTHENTICATEV2
        body = {'email':user,'password':password}
        print(loginURL)
        req = requests.post(loginURL,json=body)
        print(req.status_code)
        atoken = req.cookies.get_dict()
        print(atoken)
        if req.status_code==200:
            writeConfig(host,user,atoken.get('ATOKEN'))
            return True,atoken.get('ATOKEN')
        else:
            print("Error Handling Login")
            return False,""
    else:
        #Debug
        print("Not Valid User")
        return False,""
