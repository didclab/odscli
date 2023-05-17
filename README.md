OneDataShare Python Command Line Interface
==========

Installation & Setup
-------
#TODO
**Require Packages,**
pip3 install -r requirements.txt
**Quick Install VIA PIP,**
**Remove interactive features,**

**Examples**
```python
python3 onedatashare.py transfer s3 us-east-2:::testbucket "/" -f folderOrFileAnyNumber/ sftp ccTacc /home/cc/certs --concurrency=6 --pipesize=10
```

**Extended functionalities**

***Transfer***

You can now save your transfer command options. This feature includes the addition of a new flag called "--save," which allows you to save your command options with a chosen name. 
By providing a name along with the "--save" option, the command will be stored under that specific name for future reference.

Example :
> python3 onedatashare.py transfer googledrive my_gdrive_cred / -f "my_folder/file1.txt my_folder/file2.txt"  s3 my_s3_cred my_bucket/folder/ --concurrency=4 --pipesize=8 --parallel=0 --chunksize=10 --compress=True --encrypt=True --overwrite=True --retry=3 --verify=True --save=abc


To access a saved command, use "--config" option with the transfer command. 
Include the name under which you saved the command as a parameter with the "--config" option. 
This will allow you to retrieve and execute the previously saved command.

Example:
> python3 onedatashare.py transfer --config=abc

***Query***

You can now save the results of the query command using the "--experiment_file" flag. 
When using this flag, specify the desired name for saving your results. 
The results will be stored as a CSV file in your current directory, allowing for easy access and analysis of the retrieved data.

Example:
> python3 onedatashare.py query --job_id=13450 --experiment_file=abc
