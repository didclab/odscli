import os

import numpy as np
import pandas as pd
from sdk.meta_query import MetaQueryAPI
from tabulate import tabulate
from datetime import datetime
import time
from pathlib import Path
import csv
from sdk.log import Log
import plotext as plt

# STARTING, STARTED, STOPPING,
# STOPPED, FAILED, COMPLETED, ABANDONED

COMPLETED = "COMPLETED"
csv_headers = ['jobId', 'jobSize (MB)', 'totalSeconds', 'throughput (Mbps)', 'concurrency', 'parallelism', 'pipelining',
               'sourceType', 'destType']


class QueryGui:

    def __init__(self):
        self.mq = MetaQueryAPI()
        self.retry = 3
        self.total_sent = []
        self.influx_df = pd.DataFrame
        self.job_batch_df = pd.DataFrame
        self.files_df = pd.DataFrame
        self.job_size = 0
        self.log = Log()

    def monitor(self, job_id, delta_t, output_file):
        max_retry = 5
        if job_id is None:
            # get the last job_id listed from the query
            job_ids = self.mq.query_all_jobs_ids()
            job_id = job_ids[-1]  # get most recent jobId
        print('Monitoring jobId', job_id, "every:", delta_t, 'sec')
        if output_file is not None:
            print("Saving contents to: ", output_file)

        influx_job_data = self.mq.query_job_id_influx(job_id)
        if len(influx_job_data) > 0:
            self.log.visualize_influx_data(influx_job_data)

        local_retry = 0
        end_monitor = False
        while end_monitor is False and local_retry < max_retry:
            resp = self.mq.monitor(job_id=job_id)
            job_batch_cdb = resp.json()['jobData']
            job_data_influx = resp.json()['measurementData']
            if 'endTime' not in job_batch_cdb:
                job_batch_cdb['endTime'] = None

            if len(job_batch_cdb) > 1:
                self.log.visualize_job(job_batch_cdb)
                self.log.visualize_steps(job_batch_cdb)
            else:
                print("Failed to get Job MetaData retry:", local_retry, " max retry:", max_retry)
                local_retry += 1
                time.sleep(delta_t)
                continue

            if len(job_data_influx) < 1:
                print('Influx has no measurements of jobId: ', job_id)
                local_retry += 1
            else:
                self.log.visualize_influx_data(job_data_influx)

            if Log.check_if_job_done(job_batch_cdb['status']):
                print('\n JobId: ', job_id, ' has final status of ', job_batch_cdb['status'])
                self.finished_job_stdout(batch_job_cdb=job_batch_cdb, output_file=output_file, job_id=job_id)
                return

            if local_retry == 9:
                print('Failed to monitor transfer ')
            time.sleep(delta_t)

    def list_job_ids(self):
        job_ids = self.mq.query_all_jobs_ids()
        df = pd.DataFrame(job_ids, columns=['Job_Ids'])
        print(tabulate(df, headers='keys', tablefmt='psql'))

    def get_data(self, start_date, influx_only, cdb_only, job_id, all, list_job_ids, end_date):
        transfer_url = os.getenv('TRANSFER_SERVICE_URL')
        print("Querying CDB: ", cdb_only, " Querying Influx: ", influx_only)
        start_date = self.parse_time(start_date)
        end_date = self.parse_time(end_date)
        job_batch_json = ""
        job_influx_json = ""
        if list_job_ids is True:
            self.list_job_ids()
            return
        if cdb_only is True and influx_only is True:
            if job_id is not None and int(job_id) > 0:
                if transfer_url is None:
                    job_batch_json = self.mq.query_job_id_cdb(job_id)
                else:
                    job_batch_json = self.mq.query_transferservice_direct(job_id, transfer_url)
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

        if cdb_only:
            if len(job_batch_json) > 0:
                self.log.visualize_job(job_batch_json)
                self.log.visualize_steps(job_batch_json)

        if influx_only:
            if len(job_influx_json) > 0:
                self.log.visualize_influx_data(job_influx_json)

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

    def finished_job_stdout(self, batch_job_cdb, output_file, job_id):

        df = pd.json_normalize(batch_job_cdb)
        job_size = (int(batch_job_cdb['jobParameters']['jobSize']) / 1000000) * 8  # convert Bytes to MB then to Mb
        self.job_batch_df = self.transform_start_end_last(df)
        concurrency = batch_job_cdb['jobParameters']['concurrency']
        parallelism = batch_job_cdb['jobParameters']['parallelism']
        pipelining = batch_job_cdb['jobParameters']['pipelining']
        sourceCredType = batch_job_cdb['jobParameters']['sourceCredentialType']
        destCredType = batch_job_cdb['jobParameters']['destCredentialType']
        csv_headers = ['jobId', 'jobSizeMb', 'totalSeconds', 'throughputMbps', 'concurrency', 'parallelism',
                       'pipelining', 'sourceType', 'destType']
        totalSeconds = pd.Timedelta(
            self.job_batch_df['endTime'].tolist()[0] - self.job_batch_df['startTime'].tolist()[0]).seconds
        thrpt = job_size / totalSeconds
        if output_file is not None:
            output_path = Path(output_file)
            abs_path = output_path.expanduser()

            if not abs_path.exists():
                abs_path.parents[0].mkdir(parents=True, exist_ok=True)
                with open(abs_path, 'a+') as f:
                    csvwriter = csv.writer(f, lineterminator="\n")
                    csvwriter.writerow(csv_headers)
            csv_data = [job_id, job_size, totalSeconds, thrpt, concurrency, parallelism, pipelining, sourceCredType,
                        destCredType]
            with open(abs_path, "a+") as f:
                csvwriter = csv.writer(f, lineterminator="\n")
                csvwriter.writerow(csv_data)

        else:
            print('JobId: ', job_id)
            print('\tJob size in Megabits: ', job_size)
            print('\tTotal Time for job to complete: ', totalSeconds)
            print('\tTotal Job throughput: ', job_size / totalSeconds)

    # def pretty_print_batch_job(self, batch_job_json):
    #     # job batch information printing
    #     batch_job_cols_select = ['id', 'status', 'startTime', 'endTime', 'exitCode', 'exitMessage', 'lastUpdated']
    #     df = pd.json_normalize(batch_job_json)
    #     self.job_batch_df = self.transform_start_end_last(df)
    #     for batch_col in batch_job_cols_select:
    #         if batch_col not in self.job_batch_df:
    #             self.job_batch_df[batch_col] = np.nan
    #     print(self.job_batch_df[batch_job_cols_select].to_string())
    #
    #     # job param printing
    #     job_params = batch_job_json['jobParameters']
    #     if 'jobSize' not in job_params:
    #         job_params['jobSize'] = 0
    #     self.job_size = job_size = int(job_params['jobSize'])
    #
    #     # step information printing
    #     files_df = pd.json_normalize(batch_job_json['batchSteps'])
    #     self.files_df = self.transform_start_end_last(files_df)
    #
    #     files_cols_select = ['id', 'step_name', 'startTime', 'status', 'startTime', 'endTime']
    #     for col in files_cols_select:
    #         if col not in self.files_df:
    #             self.files_df[col] = np.nan
    #
    #     print('Total Job Size:', job_size)
    #     print("The Files in the transfer job request:\n")
    #     print(self.files_df[files_cols_select].to_string())

    # Used to keep track of total sent and the throughput achieved by summing the bytes sent and total time from startime to lastUpdated.
    # This is another interpretation of throughput. Then we can print the final throughput at the end of the job.
    # def pretty_print_influx_data(self, measurement_data_list):
    #     influx_cols_select = ['throughput', 'concurrency', 'parallelism', 'dataBytesSent',
    #                           'pipelining', 'rtt', 'dropin', 'dropout']
    #     influx_df = pd.DataFrame.from_records(measurement_data_list)
    #     for col in influx_cols_select:
    #         if col not in influx_df:
    #             influx_df[col] = np.nan
    #     if len(measurement_data_list) > 0:
    #         print('Job Id: ', measurement_data_list[0]['jobId'])
    #     # print(influx_df[influx_cols_select].to_string())
    #
    #     if self.influx_df.empty:
    #         self.influx_df = influx_df
    #     else:
    #         self.influx_df = pd.concat([self.influx_df, influx_df])
    #         self.influx_df = self.influx_df.drop_duplicates().reset_index(drop=True)
    #         self.influx_df = self.influx_df.dropna(thresh=2)
    #     bytes_sent_so_far = self.influx_df['dataBytesSent'].sum()
    #     remaining_bytes = self.job_size - bytes_sent_so_far
    #     avg_throughput = self.influx_df['throughput'].mean()
    #     remainingTime = 0
    #     if remaining_bytes == 0:
    #         print('Final influx call gives avg throughput unparsed: ', avg_throughput)
    #     else:
    #         remainingTime = remaining_bytes / avg_throughput
    #
    #     print("Job Size: ", self.job_size, " Bytes sent so far ", bytes_sent_so_far, " Bytes Remaining: ",
    #           remaining_bytes)
    #     print('Average throughput unparsed: ', avg_throughput, 'bytes/second', 'Avg Thrpt: ', avg_throughput * 8,
    #           ' bits/second', ' Parsed throughput: ', ((avg_throughput / 1000000) * 8), 'Mbps')
    #     print("Time remaining: ", remainingTime)

    def transform_start_end_last(self, df):
        if 'startTime' in df.columns:
            df['startTime'] = pd.to_datetime(df['startTime'])
        if 'endTime' in df.columns is not None:
            df['endTime'] = pd.to_datetime(df['endTime'])
        if 'lastUpdated' in df.columns:
            df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
        return df

