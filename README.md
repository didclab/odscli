OneDataShare Python Command Line Interface
==========

Installation & Setup
-------
#TODO
**Require Packages**

**Quick Install**
Files to be aware of
----
The following files consist of what could be considered the ODS Python SDK and a Python Command Line Interface to that SDK.

```
.
└── ods-cli
    └── odscli.py
    └── CredentialService.py
    └── Endpoint.py
    └── tokenUtils.py
    └── constants.py


```
Gettings Started
------
**General help**
```
~python3 odscli.py --help

```
**Command reference**
```
{ login, addRemote, listRemotes, mkdir, list }
```
**Command help**
```
~python3 odscli.py [Command] --help

[e.g. ~python3 odscli.py login --help]
```
**login**
```
-user ODS Account User Email
-pass Password for ODS Account
-host Hostname for the ODS backend to connect to

[ e.g. ~python3 odscli.py login -user myuser@onedatashare.org -password wordpass -host onedatashare.org ]

```
**addRemote**
```
-user user login for remote
-pass user password for remote
-host hostname for remote
-type type of endpoint
-path starting path for endpoint

[ e.g. ~python3 odscli.py addRemote -user myuser -pass wordpass -host localhost -type ftp -path /home ]
```
**listRemotes**
```
-type type you wish to list

```
**listRemotesEndpoint**
```
-type type you wish to list

```
**mkdir**
```
: This is the type indicator for mkdir
remote@path here you will put your remote and path

```
**list**
```
:
remote@path

```
