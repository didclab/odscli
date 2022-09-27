import pandas as pd
from datetime import datetime

class Log:
    def print_data(self, data):
        output = {}
        data_cols = ["id", "createTime", "startTime", "endTime"]
        if not data:
            print("\t None")
        for col in data_cols:
            if col in data:
                output[col] = data[col]
        if "batchSteps" in data:
            batchSteps_cols = ["step_name", "status"]
            batchSteps = {}
            for step in data["batchSteps"]:
                batchstep_id = {}
                id = step["id"]
                for col in batchSteps_cols:
                    if col in step:
                        batchstep_id[col] = step[col]
                if step[col] != "COMPLETED":
                    if "exitMessage" in step and step["exitMessage"]:
                        batchstep_id["exitMessage"] = step["batchstep_id"]
                batchstep_id["startTime"] = step["startTime"]
                batchstep_id["endTime"] = step["endTime"]
                batchstep_id["timeTaken"] = self.time_difference(step["startTime"], step["endTime"])
                batchSteps[id] = batchstep_id
            output["batchSteps"] = batchSteps
        if "jobParameters" in data:
            jobParameters = data["jobParameters"]
            jobParameters_col = ["ownerId", "size", "destBasePath", "sourceBasePath", "sourceCredentialType", "time", "fileSizeAvg"]
            for col in jobParameters_col:
                if col in jobParameters and jobParameters[col]:
                    output[col] = jobParameters[col]
        if "status" in data:
            output["status"] = data["status"]
            if data["status"] == "FAILED":
                output["exitCode"] = data["exitCode"]
            if data["exitMessage"]:
                output["exitMessage"] = data["exitMessage"]
        for key, value in output.items():
            if key == "batchSteps":
                for id, step_value in value.items():
                    print("\t ID: ", id)
                    for col, id_value in step_value.items():
                        print("\t\t", col, ": ", id_value)
            else:
                print("\t", key, ": ", value)

    def time_difference(self, start_time, end_time):
        start_date_time_obj = datetime.fromisoformat(start_time.split("+")[0])
        end_date_time_obj = datetime.fromisoformat(end_time.split("+")[0])
        tdelta = end_date_time_obj - start_date_time_obj
        return tdelta.total_seconds()