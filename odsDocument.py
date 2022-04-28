def addRemote():
    doc = '''
    ---[Command: addRemote]---

    **Description**:
        Add remote into the OneDataShare Service. And then you can make transfer
        bewtwwen different remotes

        Note add Remotes before making any transfer

    **Usage**:
        onedatashare.py addRemote (<user> (--pass=<pass> | --keyfile=<keyfile>) <host> <type>)

        Example on SFTP:
            onedatashare.py addRemote username --keyfile /.../../abc.pem hostname sftp
    
    **Flags**:
        --credentialId    make your own name on this remote, format: [--credentialId customname]

    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def lsRemote():
    doc = '''
    ---[Command: lsRemote]---

    **Description**:
        Show all the exisiting remotes by selected type, If no exisiting remote it will give
        empty

    **Usage**:
        onedatashare.py lsRemote <type>
    
        Example on SFTP:
            onedatashare.py lsRemote sftp

    **Flags**:
        Current doesn't have any flags support on this

    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def ls():
    doc = '''
    ---[Command: ls]---

    **Description**:
        List the List operation on a remote that has been added to onedatashare. 
        This requires a credential Id and a type, the path is optional.

    **Usage**:
        onedatashare.py ls <credId> <type>
        
        Example on SFTP:
            onedatashare.py ls credentialId sftp
 
    **Flags**:
        [--path=<path>]                 A string that is the parent of all the resources we are covering in the operation. 
                                        Many times this can be empty [default: ].  formate: --path path
        [--toDelete=<DELETE>]           TODO
        [--folderToCreate=<DIR>]        TODO
        [--jsonprint]                   A boolean flag to print out the response in json [default: ""].   formate: --jsonprint
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def rm():
    doc = '''
    ---[Command: rm]---

    **Description**:
        Remove operation on an added server. Requires a credential Id, type, and a path(either folder or file).
        If a directory is passed then it will recursively delete the directory

    **Usage**:
        onedatashare.py rm <credId> <type>
        
        Example on SFTP:
            onedatashare.py rm credentialId sftp


    **Flags**:
        [--path=<path>]                 A string that is the parent of all the resources we are covering in the operation. 
                                        Many times this can be empty [default: ].  formate: --path path
        [--toDelete=<DELETE>]           TODO
        [--folderToCreate=<DIR>]        TODO
        [--jsonprint]                   A boolean flag to print out the response in json [default: ""].   formate: --jsonprint
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def mkdir():
    doc = '''
    ---[Command: mkdir]---

    **Description**:
        Creates a directory on an added server.
        This requires credential Id, type, and a path to create

    **Usage**:
        onedatashare.py mkdir <credId> <type>
        
        Example on SFTP:
            onedatashare.py mkdir credentialId sftp

    **Flags**:
        [--path=<path>]                 A string that is the parent of all the resources we are covering in the operation. 
                                        Many times this can be empty [default: ].  formate: --path path
        [--toDelete=<DELETE>]           TODO
        [--folderToCreate=<DIR>]        TODO
        [--jsonprint]                   A boolean flag to print out the response in json [default: ""].   formate: --jsonprint
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def transfer():
    doc = '''
    ---[Command: transfer]---

    **Description**:
        Submits a transfer job to onedatashare.org. Requires a Source(credentialID, type, source path, list of files), Destination(type, credential ID, destination path).
        The Transfer options are the following:
            compress, optimize(in-progress), encrypt(in-progress), overwrite(in-progress),
            retry, verify, concurrencyThreadCount(server and protocol restrictions apply),
            parallelThreadCount(not supported on protocols that dont support seek()), pipeSize, chunkSize, test

    **Usage**:
        onedatashare.py transfer (<source_type> <source_credid> <source_path> (-f FILES)... <dest_type> <dest_credid> <dest_path>)

        Example VFS transfer to SFTP:
            onedatashare.py transfer vfs source-credid /../../path -f transferFile sftp dest-credid /../../path

    **Flags**:
        --concurrency           The number of concurrent connections you wish to use on your transfer [default: 1]
        --pipesize              The amount of reads or writes to do. read # and write # [default: 10]
        --parallel              The number of parallel threads to use for every concurrent connection
        --chunksize             The number of bytes for every read operation default is 64KB [default: 64000]
        --compress              A boolean flag that will enable compression. This currently only works for SCP, SFTP, FTP. [default: False]
        --encrypt               A boolean flag to enable encryption. Currently not supported [default: False]
        --optimize              A string flag that allows the user to select which form of optimization to use. [default: False]
        --overwrite             A boolean flag that will overwrite files with the same path as found on the remote. Generally I would not use this [default: False]
        --retry                 An integer that represents the number of retries for every single file. Generally I would keep this below 10 [default: 5]
        --verify                A boolean flag to flag the use of checksumming after every file or after the whole job. [default: False]
        --repeat                An integer to represents the number of repeat time will run for transfer. [default: 1]
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def query():
    doc = '''
    **Description**:

    **Usage**:

    **Flags**:
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def testAll():
    doc = '''
    ---[Command: testAll]---

    **Description**:
        Submit a transfer job with test purpose to all existing remotes.
        it requires remote type, remote id, file path, file and destination path

    **Usage**:
        onedatashare.py testAll (<source_type> <source_credid> <source_path> (-f FILES)... <dest_path>)
            
        Example AmazonS3 transfer to All:
            onedatashare.py testAll s3 source-credid /../../path -f transferFile /../../path

    **Flags**:
        --concurrency           The number of concurrent connections you wish to use on your transfer [default: 1]
        --pipesize              The amount of reads or writes to do. read # and write # [default: 10]
        --parallel              The number of parallel threads to use for every concurrent connection
        --chunksize             The number of bytes for every read operation default is 64KB [default: 64000]
        --compress              A boolean flag that will enable compression. This currently only works for SCP, SFTP, FTP. [default: False]
        --encrypt               A boolean flag to enable encryption. Currently not supported [default: False]
        --optimize              A string flag that allows the user to select which form of optimization to use. [default: False]
        --overwrite             A boolean flag that will overwrite files with the same path as found on the remote. Generally I would not use this [default: False]
        --retry                 An integer that represents the number of retries for every single file. Generally I would keep this below 10 [default: 5]
        --verify                A boolean flag to flag the use of checksumming after every file or after the whole job. [default: False]
        --repeat                An integer to represents the number of repeat time will run for transfer. [default: 1]
    
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def rc_transfer():
    doc = '''
    ---[Command: rc_transfer]---

    **Description**:
        Use rClone to submit a transfer from one remote to another remote, if destination path is not exist
        it will create a folder and then make transfer file. It requires rclone source remote id, source path, file,
        rclone destination remote id and destination path
        
        Note: You need add remote in your local machine by rclone command first.
              Every id is stand by rclone remote id

    **Usage**:
        onedatashare.py rc_transfer <source_credid> <source_path> <file> <dest_credid> <dest_path>

        Example SFTP to SFTP:
            onedatashare.py rc_transfer source-rclone-id /../../path fileName destination-rclone-id /../../path

    **Flags**:
        --process           Shows up live process for transfer (rc_command only) [default: False]. Format --process
        --repeat            An integer to represents the number of repeat time will run. [default: 1].  Format --repeat 5
        --all               Make current command from one to one to be one to all model (existing remote),
                            it will send file to all remotes in destination path [default: False].  Format: --all
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def rc_delete():
    doc = '''
    ---[Command: rc_delete]---

    **Description**:
        Use rClone to delete specifc file that existing in the remote, if apply all option
        then it will delete all remotes in same directory and file.

        Note: You need add remote in your local machine by rclone command first.
              Every id is stand by rclone remote id

    **Usage**:
        onedatashare.py rc_delete <source_credid> <path> <file>

        Example on SFTP:
            onedatashare.py rc_delete rclone-id /../../path fileName

    **Flags**:
         --all       Make current command from one to one to be one to all model (existing remote)
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def rc_lsRemote():
    doc = '''
    ---[Command: rc_lsRemote]---

    **Description**:
        List the existing remotes in the rclone

    **Usage**:
        onedatashare.py rc_lsRemote
        
        Example on SFTP:
            onedatashare.py rc_lsRemote

    **Flags**:
    
    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc

def other():
    doc = '''
    
    we don't support on this command, please check anything else.

    Use "python3 onedatashare help [command]" for more information about a command.
    '''
    return doc