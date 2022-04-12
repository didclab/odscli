"""
Things to know when writing:
<> = WORDSINCAPS    stand for arguments and do not require flags just write the values in order
[]                  stand for optional arguments or anything within the braces is optional
--                  According to POSIX std all arguments are positional arguments even tho they might look like options
-                   Program will take input from std input vs from file. Not hard std of POSIX

Usage:
  rclone.py transfer <source_credid> <source_path> <file> <dest_credid> <dest_path> [--process --repeat=<times>]
  rclone.py transferAll <source_credid> <source_path> <file> <dest_path> [--process --repeat=<times>]
  rclone.py deleteAllFile <path> <file>
  rclone.py deleteFile <source_credid> <path> <file>
  rclone.py lsRemote
  

Commands:
  transfer      Transfer source file to destination
  transferAll   Transfer source file to all existing remote
  lsRemote      List all existing remote in the rclone

Options:
  --process            Shows up live process for transfer [default: False]
  --repeat=<times>     Make transfer/transferAll repeat K times [default: 1]
"""
# from concurrent.futures import process
from fileinput import filename
import subprocess
from sys import stderr
import rclone
import sys

from docopt import docopt
import os

dict = {"transfer": "copy", "deleteFile": "deletefile"}
options_dict = {}

def lsRemote():
    with subprocess.Popen(["rclone","listremotes"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            (out, err) = process.communicate()
    list = out.decode("utf-8").split("\n")
    print("")
    return list[:-1]

def transfer(command, source_credid, source_path, file, dest_credid, dest_path, process=False, repeat=1):
    if(source_credid[-1] != ':'):
        source_credid = source_credid+":"
    if(dest_credid[-1] != ':'):
        dest_credid = dest_credid+":"
    arg1 = source_credid+source_path+"/"+file
    arg2 = dest_credid+dest_path
    if process: process = "-P"
    else: process = ""
    print(dest_credid + " -------------------------------------------------------------------------------------------")
    cml = "rclone" + " " + command + " " + arg1 + " " + arg2 + " " + str(process)
    os.system(cml)
    # os.system("rclone copy "+arg1+" "+arg2)
    print(" ")
    return

def deleteFile(command, dest_credid, path, file):
    if(dest_credid[-1] != ':'):
        dest_credid = dest_credid+":"
    target = path + "/" + file
    cml = "rclone" + " " + command + " " + dest_credid + target
    os.system(cml)

def checkFile(dest_credid, path, file):
    arg1 = dest_credid+ path
    with subprocess.Popen(["rclone", "lsf",arg1], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            (out, err) = process.communicate()
    file_list = out.decode("utf-8").split("\n")
    for info in file_list:
        if info == file:
            return True
    return False



if __name__ == '__main__':
    args = docopt(__doc__, version='Naval Fate 2.0')
    print(args)
    if args['lsRemote']:
        lsRemote()
    elif args['transfer']:
        times = int(args["--repeat"])
        transfer(dict["transfer"], args["<source_credid>"], args["<source_path>"],args["<file>"], args["<dest_credid>"],args["<dest_path>"], process=args["--process"])
    elif args['transferAll']:
        times = int(args["--repeat"])
        remotes = lsRemote()
        source, source_path, file_name, dest_path = args["<source_credid>"], args["<source_path>"], args["<file>"], args["<dest_path>"]
        for j in range(0, times):
            for i in remotes:
                if i !=source+":":
                    if checkFile(i, dest_path, file_name): 
                        print("delete file successful")
                        deleteFile(dict['deleteFile'], i, dest_path, file_name)
                    transfer(dict["transfer"], source, source_path, file_name, i, dest_path, process=args["--process"])
    elif args['deleteAllFile']:
        remotes = lsRemote()
        path, file_name = args['<path>'], args['<file>']
        for i in remotes:
            deleteFile(dict['deleteFile'], i, path, file_name)
    elif args['deleteFile']:
        source, path, file_name = args['<source_credid>'], args['<path>'], args['<file>']
        deleteFile(dict['deleteFile'],source, path, file_name)