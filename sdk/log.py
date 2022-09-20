import pandas as pd

class Log:
    def print_data(self, data):
        output = {}
        if not data:
            print("\t None")
        if "id" in data:
            output["id"] = data["id"]
        if "createTime" in data:
            output["createTIme"] = data["createTime"]
        if "startTime" in data:
            output["startTime"] = data["startTime"]
        if "endTime" in data:
            output["endTime"] = data["endTime"]
        if "jobParameters" in data:
            jobParameters = data["jobParameters"]
            if "ownerId" in jobParameters:
                output["ownerId"] = jobParameters["ownerId"]
            if "size" in jobParameters:
                output["size"] = jobParameters["size"]
            if "destBasePath" in jobParameters and jobParameters["destBasePath"]:
                output["dataBasePath"] = jobParameters["dataBasePath"]
            if "sourceBasePath" in jobParameters and jobParameters["sourceBasePath"]:
                output["sourceBasePath"] = jobParameters["sourceBasePath"]
            if "sourceCredentialType" in jobParameters and jobParameters["sourceCredentialType"]:
                output["sourceCredentialType"] = jobParameters["sourceCredentialType"]
            if "time" in jobParameters:
                output["time"] = jobParameters["time"]
            if "fileSizeAvg" in jobParameters:
                output["fileSizeAvg"] = jobParameters["fileSizeAvg"]
        if "status" in data:
            output["status"] = data["status"]
            if data["status"] == "FAILED":
                output["exitCode"] = data["exitCode"]
            if data["exitMessage"]:
                output["exitMessage"] = data["exitMessage"]
        for key, value in output.items():
            print("\t", key, ": ", value)
