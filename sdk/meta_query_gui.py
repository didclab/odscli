import numpy as np
import pandas as pd
from sdk.meta_query import MetaQueryAPI
from tabulate import tabulate
from datetime import datetime
import time
from pathlib import Path
import pprint
import csv
from sdk.log import Log
import plotext as plt
# STARTING, STARTED, STOPPING,
# STOPPED, FAILED, COMPLETED, ABANDONED

COMPLETED = "COMPLETED"
#                print('\tJob size in Megabits: ', job_size, file=f)
#                print('\tTotal Time for job to complete: ', totalSeconds, file=f)
#                print('\tTotal Job throughput: ', job_size / totalSeconds, 'Mbps', file=f)

csv_headers = ['jobId', 'jobSize (MB)', 'totalSeconds', 'throughput (Mbps)', 'concurrency', 'parallelism', 'pipelining', 'sourceType', 'destType']


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

    def job_start(self, job_id, delta_t):
        job_start_retry = 0
        batch_job_json = self.mq.query_job_id_cdb(job_id)
        while job_start_retry < 10:
            if self.has_job_started(batch_job_json):
                print('Job ', job_id, ' has Started!')
                return batch_job_json
            batch_job_json = self.mq.query_job_id_cdb(job_id)
            job_start_retry += 1
            if job_start_retry > 5:
                return None
            time.sleep(delta_t)
        if len(batch_job_json) > 1:
            self.pretty_print_batch_job(batch_job_json)  # get the job table from the backend which gives start time and each steps start time
        return batch_job_json

    def monitor(self, job_id, delta_t, output_file):
        print('output times to ', output_file)
        max_retry = 5
        print('monitoring', job_id, "every:", delta_t, 'sec')
        if job_id is None:
            # get the last job_id listed from the query
            job_ids = self.mq.query_all_jobs_ids()
            job_id = job_ids[-1]  # get most recent jobId

        self.job_start(job_id, delta_t)  # check if job has started if so print before loop

        influx_job_data = self.mq.query_job_id_influx(job_id)
        if len(influx_job_data) > 0:
            self.pretty_print_influx_data(influx_job_data)  # print what we achomplished before monitoring

        local_retry = 0
        end_monitor = False
        while end_monitor is False and local_retry < max_retry:
            # resp = self.mq.monitor(job_id=job_id)
            job_batch_cdb = self.mq.query_job_id_cdb(job_id)
            job_data_influx = self.mq.query_job_id_influx(job_id)
            if len(job_batch_cdb) < 1:
                print(job_batch_cdb)
                print('Failed to get job batch table information retry: ', local_retry, '/', max_retry)
                local_retry += 1
                # time.sleep(delta_t)
                # continue
            else:
                self.pretty_print_batch_job(job_batch_cdb)
                if len(job_data_influx) < 1:
                    print(job_data_influx)
                    print('No Monitoring data yet')
                    # time.sleep(delta_t)
                    # continue
                else:
                    self.pretty_print_influx_data(job_data_influx)

            if self.check_if_job_done(job_batch_cdb['status']):
                print('\n', job_id, ' has final status of ', job_batch_cdb['status'])
                self.finished_job_stdout(batch_job_cdb=job_batch_cdb, output_file=output_file, job_id=job_id)
                return

            if local_retry == 9:
                print('Failed to monitor transfer ')
            time.sleep(delta_t)

    def has_job_started(self, batch_job_json):
        if 'endTime' in batch_job_json:
            return True
        if 'startTime' in batch_job_json:
            return True
        else:
            return False

    def check_if_job_done(self, status):
        if status == "COMPLETED" or status == "FAILED" or status == "ABANDONED" or status == "STOPPED":
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

        print("1. Complex/Complete data")
        print("2. Simple data")
        option = input("Select one of the above options regarding the data: ")
        if option not in ["1", "2"]:
            print("Invalid option")
            return
        print("Job Batch Data: ")
        if option == "1":
            print(job_batch_json)
        elif option == "2":
            self.log.print_data(job_batch_json)
        print("Influx Measurements Data:")
        if option == "1":
            print(job_influx_json)
        elif option == "2":
            self.pretty_print_influx_data(job_influx_json)

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
        csv_headers = ['jobId', 'jobSize (MB)', 'totalSeconds', 'throughput (Mbps)', 'concurrency', 'parallelism',
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
            csv_data = [job_id, job_size, totalSeconds, thrpt, concurrency, parallelism, pipelining, sourceCredType, destCredType]
            with open(abs_path, "a+") as f:
                csvwriter = csv.writer(f, lineterminator="\n")
                csvwriter.writerow(csv_data)
                # print('***** JobId: ', job_id, file=f)
                # print('\tJob size in Megabits: ', job_size, file=f)
                # print('\tTotal Time for job to complete: ', totalSeconds, file=f)
                # print('\tTotal Job throughput: ', thrpt, 'Mbps', file=f)

        else:
            print('***** JobId: ', job_id)
            print('\tJob size in Megabits: ', job_size)
            print('\tTotal Time for job to complete: ', totalSeconds)
            print('\tTotal Job throughput: ', job_size / totalSeconds)

    # 'id', 'version', 'step_name', 'jobInstanceId', 'startTime', 'endTime',
    #       'status', 'commitCount', 'readCount', 'filterCount', 'writeCount',
    #       'readSkipcount', 'writeSkipCount', 'processSkipCount', 'rollbackCount',
    #       'exitCode', 'exitMessage', 'lastUpdated
    def pretty_print_batch_job(self, batch_job_json):
        # job batch information printing
        batch_job_cols_select = ['id', 'status', 'startTime', 'endTime', 'exitCode', 'exitMessage', 'lastUpdated']
        df = pd.json_normalize(batch_job_json)
        self.job_batch_df = self.transform_start_end_last(df)
        for batch_col in batch_job_cols_select:
            if batch_col not in self.job_batch_df:
                self.job_batch_df[batch_col] = np.nan
        print(self.job_batch_df[batch_job_cols_select].to_string())

        # job param printing
        job_params = batch_job_json['jobParameters']
        if 'jobSize' not in job_params:
            job_params['jobSize'] = 0
        self.job_size = job_size = int(job_params['jobSize'])

        # step information printing
        files_df = pd.json_normalize(batch_job_json['batchSteps'])
        self.files_df = self.transform_start_end_last(files_df)

        files_cols_select = ['id', 'step_name', 'startTime', 'status', 'startTime', 'endTime']
        for col in files_cols_select:
            if col not in self.files_df:
                self.files_df[col] = np.nan

        print('Total Job Size:', job_size)
        print("The Files in the transfer job request:\n")
        print(self.files_df[files_cols_select].to_string())

    # Used to keep track of total sent and the throughput achieved by summing the bytes sent and total time from startime to lastUpdated.
    # This is another interpretation of throughput. Then we can print the final throughput at the end of the job.
    def pretty_print_influx_data(self, measurement_data_list):
        influx_cols_select = ['throughput', 'concurrency', 'parallelism', 'dataBytesSent',
                              'pipelining', 'rtt', 'dropin', 'dropout']
        influx_df = pd.DataFrame.from_records(measurement_data_list)
        for col in influx_cols_select:
            if col not in influx_df:
                influx_df[col] = np.nan
        if len(measurement_data_list) > 0:
            print('Job Id: ', measurement_data_list[0]['jobId'])
        print(influx_df[influx_cols_select].to_string())

        if self.influx_df.empty:
            self.influx_df = influx_df
        else:
            self.influx_df = pd.concat([self.influx_df, influx_df])
            self.influx_df = self.influx_df.drop_duplicates().reset_index(drop=True)
            self.influx_df = self.influx_df.dropna(thresh=2)
        bytes_sent_so_far = self.influx_df['dataBytesSent'].sum()
        remaining_bytes = self.job_size - bytes_sent_so_far
        avg_throughput = self.influx_df['throughput'].mean()
        remainingTime = 0
        if remaining_bytes == 0:
            print('Final influx call gives avg throughput unparsed: ', avg_throughput)
        else:
            remainingTime = remaining_bytes / avg_throughput

        print("Job Size: ", self.job_size, " Bytes sent so far ", bytes_sent_so_far, " Bytes Remaining: ",
              remaining_bytes)
        print('Average throughput unparsed: ', avg_throughput, 'bytes/second', 'Avg Thrpt: ', avg_throughput * 8,
              ' bits/second', ' Parsed throughput: ', ((avg_throughput / 1000000) * 8), 'Mbps')
        print("Time remaining: ", remainingTime)

        self.plot_graphs(influx_df)

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

    def plot_graphs(self, influx_df):
        print("\n")
        time = [x for x in range(influx_df.shape[0])]
        time_labels = [x for x in range(0, influx_df.shape[0], 3)]
        plt.subplots(2, 1)

        plt.subplot(1, 1).plot_size(2*plt.tw()/3, plt.th()/3)
        y = [x/1e6 for x in influx_df['throughput']]
        plt.subplot(1, 1).plot(time, y)
        plt.subplot(1, 1).xlabel("Time(s)")
        plt.subplot(1, 1).ylabel("Throughput(Mbps)")
        plt.subplot(1, 1).xticks(time_labels)
        plt.subplot(1, 1).title("Throughput Plot")

        plt.subplot(2, 1).plot_size(2*plt.tw()/3, plt.th()/3)
        plt.subplot(2, 1).plot(influx_df['parallelism'], label = "Parallelism")
        plt.subplot(2, 1).plot(influx_df['concurrency'], label = "Concurrency")
        plt.subplot(2, 1).plot(influx_df['pipelining'], label = "Pipelining")
        plt.subplot(2, 1).xlabel("Time(s)")
        plt.subplot(2, 1).xticks(time_labels)
        plt.show()
