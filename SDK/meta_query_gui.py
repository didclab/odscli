import numpy as np
import pandas as pd
from SDK.meta_query import MetaQueryAPI
from tabulate import tabulate
from datetime import datetime
import time
import pprint

# STARTING, STARTED, STOPPING,
# STOPPED, FAILED, COMPLETED, ABANDONED

COMPLETED = "COMPLETED"


class QueryGui:

    def __init__(self):
        self.mq = MetaQueryAPI()
        self.retry = 3
        self.total_sent = []
        self.influx_df = pd.DataFrame
        self.job_batch_df = pd.DataFrame
        self.files_df = pd.DataFrame
        self.job_size = 0

    def monitor(self, job_id, delta_t):
        if job_id is None:
            # get the last job_id listed from the query
            job_ids = self.mq.query_all_jobs_ids()
            job_id = job_ids[-1]
        print('monitoring', job_id, "every:", delta_t, 'sec')
        end_monitor = False
        batch_job_json = self.mq.query_job_id_cdb(job_id)
        if len(batch_job_json) > 1:
            self.pretty_print_batch_job(batch_job_json)  # get the job table from the backend which gives start time and each steps start time

        initial_measurements = self.mq.query_job_id_influx(
            job_id)  # this is here incase the user calls monitoring much later than job start time. It will get all measurements at first

        if len(initial_measurements) > 0:
            self.pretty_print_influx_data(initial_measurements)

        local_retry = 0

        while end_monitor is False and local_retry < 3:
            resp = self.mq.monitor(job_id=job_id)
            if not resp.ok:
                local_retry += 1
                continue
            if len(resp.json()) == 0:
                local_retry += 1
                continue
            if not batch_job_json:
                continue
            job_batch_cdb = resp.json()['jobData']
            if self.check_if_job_done(job_batch_cdb['status']):
                print('Job Completed and took a total time')
                self.pretty_print_batch_job(job_batch_cdb)
                return
            print('\n')
            job_data_influx = resp.json()['measurementData']
            self.pretty_print_influx_data(job_data_influx)

            if self.check_if_job_done(resp.json()):
                end_monitor = True

            self.pretty_print_batch_job(batch_job_json=job_batch_cdb)

            if local_retry > 3:
                return

            time.sleep(int(delta_t))

    def has_job_started(self, batch_job_json):
        if 'startTime' not in batch_job_json:
            return False
        return True
    def check_if_job_done(self, status):
        if status == "COMPLETED" or status == "FAILED" or status == "ABANDONED" or status == "STOPPED" or status == "STOPPING":
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

    # 'id', 'version', 'step_name', 'jobInstanceId', 'startTime', 'endTime',
    #       'status', 'commitCount', 'readCount', 'filterCount', 'writeCount',
    #       'readSkipcount', 'writeSkipCount', 'processSkipCount', 'rollbackCount',
    #       'exitCode', 'exitMessage', 'lastUpdated
    def pretty_print_batch_job(self, batch_job_json):
        batch_job_cols_select = ['id', 'status', 'startTime', 'exitCode', 'exitMessage', 'lastUpdated']
        df = pd.json_normalize(batch_job_json)
        self.job_batch_df = self.transform_start_end_last(df)
        if 'endTime' not in batch_job_json:
            self.job_batch_df['endTime']=np.nan
        if 'startTime' not in batch_job_json:
            self.job_batch_df['endTime']=np.nan
        print(self.job_batch_df[batch_job_cols_select].to_string())

        job_params = batch_job_json['jobParameters']
        files_df = pd.json_normalize(batch_job_json['batchSteps'])
        self.files_df = self.transform_start_end_last(files_df)

        # time_delta_df = self.files_df['startTime'].sub(self.files_df['endTime'])
        # print(pd.to_datetime(self.files_df['startTime']))
        files_cols_select = ['id', 'step_name', 'startTime', 'endTime', 'readCount', 'writeCount', 'lastUpdated',
                             'status']
        self.job_size = job_size = int(job_params['jobSize'])
        print('Total Job Size:', job_size)
        print("The Files in the transfer job request:\n")
        print(self.files_df[files_cols_select].to_string())

    # Used to keep track of total sent and the throughput achieved by summing the bytes sent and total time from startime to lastUpdated.
    # This is another interpretation of throughput. Then we can print the final throughput at the end of the job.
    def pretty_print_influx_data(self, meausrement_data_list):
        influx_cols_select = ['jobId', 'throughput', 'concurrency', 'parallelism', 'dataBytesSent', 'compression',
                              'pipelining']
        influx_df = pd.DataFrame.from_records(meausrement_data_list)
        # print(influx_df[influx_cols_select].to_string())
        if self.influx_df.empty:
            self.influx_df = influx_df
        else:
            self.influx_df = pd.concat([self.influx_df, influx_df])
            self.influx_df = self.influx_df.drop_duplicates().reset_index(drop=True)
        bytes_sent_so_far = self.influx_df['dataBytesSent'].sum()
        remaining_bytes = self.job_size - bytes_sent_so_far
        avg_throughput = self.influx_df['throughput'].mean()
        remainingTime = avg_throughput/ remaining_bytes

        print("Job Size: ", self.job_size, " Bytes sent so far ", bytes_sent_so_far, " Bytes Remaining: ", remaining_bytes)
        print("Average Throughput(column) so far: ", avg_throughput)
        print("Time remaining: ", remainingTime)

    def print_finished_job(self):
        print('Job Completed with values')

    def transform_start_end_last(self, df):
        if 'startTime' in df.columns:
            df['startTime'] = pd.to_datetime(df['startTime'])
        if 'endTime' in df.columns is not None:
            df['endTime'] = pd.to_datetime(df['endTime'])
        if 'lastUpdated' in df.columns:
            df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
        return df
