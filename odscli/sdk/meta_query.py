import os

import requests
import odscli.sdk.constants as constants
import odscli.sdk.token_utils as tok

BASEPATH = "/api/metadata"
JOB = "/job"
JOB_DIRECT = "/api/v1/job"
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
        self.user = user
        self.token = token
        self.monitoring_ip = os.getenv("MONITORING_HOST", "metdatalb-1298245410.us-east-2.elb.amazonaws.com")

    def query_job_uuids(self):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + "/all/job/uuids"
        # hostStr = "http://localhost:8080" + BASEPATH + "/all/job/uuids"
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies)
        return r.json()

    def query_job_progress(self, job_uuid):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + "/progress"
        param = {"jobUuid": job_uuid}
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies, params=param)
        return r.json()

    def query_job_id_cdb(self, job_id):
        param = {"jobId": job_id}
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + JOB
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r.json()

    def query_transferservice_direct(self, job_id, transfer_url):
        param = {"jobId": job_id}
        hostStr = transfer_url + JOB_DIRECT + "/execution"
        r = requests.get(hostStr, params=param)
        return r.json()

    def query_all_jobs_ids(self):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + "/all/job/ids"
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies)  # Needs to be handled better for errors
        return sorted(r.json())

    def query_job_ids_direct(self, transfer_url):
        # http://localhost:8092
        hostStr = transfer_url + "/api/v1/job/ids"
        r = requests.get(hostStr)
        return r.json()

    def query_job_id_influx(self, job_id):
        # hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + JOB
        hostStr = "http://" + self.monitoring_ip + "/api/v1/meta/stats/influx/job"
        params = {"jobId": job_id, "userEmail": self.user}

        r = requests.get(hostStr, params=params)  # Needs to be handled better for errors
        response_json = r.json()
        if r.status_code > 400:
            return ""
        else:
            return response_json

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

    # This method needs to get used in some kind of monitor UI that I will be building out. This is merely the starting call from the cli.
    def monitor(self, job_id):
        hostStr = constants.ODS_PROTOCOL + self.host + BASEPATH + MEASUREMENTS + MONITOR
        param = {"jobId": job_id}
        cookies = dict(ATOKEN=self.token)
        headers = {"Authorization": "Bearer " + self.token + ""}
        r = requests.get(hostStr, headers=headers, cookies=cookies,
                         params=param)  # Needs to be handled better for errors
        return r
