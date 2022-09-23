import requests
import sdk.constants as constants
import sdk.token_utils as tok
BASEPATH = "/api/metadata"
JOB = "/job"
ALL = "/all"
JOB_IDS = "/jobids"
JOBS = "/jobs"
MEASUREMENT = "/measurement"
MEASUREMENTS = "/measurements"
USER = "/user"
RANGE = "/range"
MONITOR = "/monitor"


class MetaQueryAPI:
    def __init__(self):
        host, user, token = tok.readConfig()
        self.host = host
        self. user = user
        self.token = token

    def query_job_id_cdb(self, job_id):
        param = {"jobId": job_id}
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + JOB
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r.json()

    def query_all_jobs_ids(self):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + "/all/job/ids"
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies)  # Needs to be handled better for errors
        return r.json()

    def query_job_id_influx(self, job_id):
        param = {"jobId": job_id}
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + JOB
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        if r.status_code > 400:
            return ""
        else:
            return r.json()

    def all_user_stats_cdb(self):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + ALL + JOBS
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies)  # Needs to be handled better for errors
        return r.json()

    def all_user_measurements_influx(self):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + USER
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies)  # Needs to be handled better for errors
        return r.json()

    def query_range_cdb(self, start_date_time, end_date_time):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + ALL + JOBS + RANGE
        param = {"start": start_date_time, "end": end_date_time}
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r.json()

    def query_range_influx(self, start_date, end_date):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + RANGE
        param = {"start": start_date, "end": end_date}
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r.json()

    #This method needs to get used in some kind of monitor UI that I will be building out. This is merely the starting call from the cli.
    def monitor(self, job_id):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + MONITOR
        param = {"jobId": job_id}
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r
