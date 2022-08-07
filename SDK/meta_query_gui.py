import pandas as pd
from SDK.meta_query import MetaQueryAPI
from tabulate import tabulate
from datetime import datetime
import time


# STARTING, STARTED, STOPPING,
# STOPPED, FAILED, COMPLETED, ABANDONED

COMPLETED="COMPLETED"

class QueryGui:

    def __init__(self):
        self.mq = MetaQueryAPI()
        self.retry = 3

    def monitor(self, job_id, delta_t):
        print('monitoring', job_id, "every:", delta_t,'sec')
        end_monitor = False
        batch_job_data_dict = self.mq.query_job_id_cdb(job_id)
        self.pretty_print_batch_job(batch_job_data_dict)
        if len(batch_job_data_dict) == 0:
            print('Batch Job Data was empty so this job was never launched: {}', job_id)
            return
        if 'jobData' in batch_job_data_dict:
            print(self.pretty_print_batch_job(batch_job_data_dict)['jobData'])
        local_retry = 0
        while end_monitor is False:
            resp = self.mq.monitor(job_id=job_id)
            influx_data_json = resp.json()
            if not resp.ok:
                local_retry+=1
                continue
            if len(resp.json()) == 0:
                local_retry+=1
                continue
            if self.check_if_job_done(influx_data_json):
                end_monitor = True
            if local_retry > 3:
                return
            time.sleep(int(delta_t))

    def check_if_job_done(self, json_resp):
        val = json_resp['jobData']['status']
        if val == "COMPLETED" or val == "FAILED" or val == "ABANDONED" or val == "STOPPED" or val == "STOPPING":
            return True
        else:
            return False

    def list_job_ids(self):
        job_ids = self.mq.query_all_jobs_ids()
        df = pd.DataFrame(job_ids, columns=['Job_Ids'])
        print(tabulate(df, headers='keys', tablefmt='psql'))

    def get_data(self, start_date, influx_only, cdb_only, job_id, all, list_job_ids, end_date):
        start_date = self.parse_time(start_date)
        end_date = self.parse_time(end_date)
        job_batch_json = ""
        job_influx_json = ""
        print(start_date, end_date, influx_only, cdb_only, job_id, all, list_job_ids)
        if list_job_ids is True:
            self.list_job_ids()
        if cdb_only is True and influx_only is True:
            if job_id is not None and int(job_id) > 0:
                job_batch_json = self.mq.query_job_id_cdb(job_id)
                job_influx_json = self.mq.query_job_id_influx(job_id)
            elif start_date is not None and end_date is not None:
                job_batch_json = self.mq.query_range_cdb(start_date_time=self.parse_time(start_date),
                                                         end_date_time=self.parse_time(end_date))
                job_influx_json = self.mq.query_range_influx(start_date=self.parse_time(start_date),
                                                             end_date=self.parse_time(end_date))
            elif all is True:
                job_batch_json = self.mq.all_user_stats_cdb()
                job_influx_json = self.mq.all_user_measurements_influx()
        elif cdb_only is True:
            if job_id is not None and int(job_id) > 0:
                job_batch_json = self.mq.query_job_id_cdb(job_id)
            elif start_date is not None and end_date is not None:
                job_batch_json = self.mq.query_range_cdb(start_date_time=self.parse_time(start_date),
                                                         end_date_time=self.parse_time(end_date))
            elif all is True:
                job_batch_json = self.mq.all_user_stats_cdb()
        elif influx_only:
            if job_id is not None and int(job_id) > 0:
                job_influx_json = self.mq.query_job_id_influx(job_id)
            elif start_date is not None and end_date is not None:
                job_influx_json = self.mq.query_range_influx(start_date=self.parse_time(start_date),
                                                             end_date=self.parse_time(end_date))
            elif all is True:
                job_influx_json = self.mq.all_user_measurements_influx()

        # tabulate(job_batch_json)
        # tabulate(job_influx_json)
        print("Job Batch Data: ", job_batch_json)
        print("Influx Measurements Data: ", job_influx_json)

    def parse_time(self, time):
        if time is None:
            return None
        if isinstance(time, datetime):
            return time
        print('User input: ', time)
        date_time_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        print('datetime obj: ', date_time_obj)
        res = date_time_obj.utcnow().isoformat()
        print('datetime obj w/o +:', res)
        if not isinstance(time, datetime):
            print(
                "Invalid date format please do yyyy-mm-ddTHH:MM for submitting time format for start_date and end_date")
        return res

#'id', 'version', 'step_name', 'jobInstanceId', 'startTime', 'endTime',
#       'status', 'commitCount', 'readCount', 'filterCount', 'writeCount',
#       'readSkipcount', 'writeSkipCount', 'processSkipCount', 'rollbackCount',
#       'exitCode', 'exitMessage', 'lastUpdated
    def pretty_print_batch_job(self, batch_job_json):
        print('Job Information: ID')
        file_cols = ['id', 'step_name', 'startTime', 'endTime', 'readCount', 'writeCount', 'lastUpdated', 'status']
        print(batch_job_json.keys())
        files = batch_job_json['batchSteps']
        print(files.keys())
        files_df = pd.json_normalize(files)
        print(tabulate(files_df, headers='keys'))
        job_param_df = pd.json_normalize(batch_job_json['jobParameters'])

        print('\nJob Parameters: ', job_param_df)

        job_size = job_param_df['jobSize']
        print('Total Job Size:', job_size)
        steps_df = pd.json_normalize(files)
