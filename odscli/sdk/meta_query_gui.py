import pandas as pd
from odscli.sdk.meta_query import MetaQueryAPI
from pathlib import Path
import csv
from odscli.sdk.log import Log

COMPLETED = "COMPLETED"
csv_headers = ['jobId', 'jobSize (MB)', 'totalSeconds', 'throughput (Mbps)', 'concurrency', 'parallelism', 'pipelining',
               'sourceType', 'destType']


def transform_start_end_last(df):
    if 'startTime' in df.columns:
        df['startTime'] = pd.to_datetime(df['startTime'])
    if 'endTime' in df.columns is not None:
        df['endTime'] = pd.to_datetime(df['endTime'])
    if 'lastUpdated' in df.columns:
        df['lastUpdated'] = pd.to_datetime(df['lastUpdated'])
    return df


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

    def finished_job_stdout(self, batch_job_cdb, output_file, job_id):
        df = pd.json_normalize(batch_job_cdb)
        job_size = (int(batch_job_cdb['jobParameters']['jobSize']) / 1000000) * 8  # convert Bytes to MB then to Mb
        self.job_batch_df = transform_start_end_last(df)
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

        print('JobId: ', job_id)
        print('\tJob size in Megabits: ', job_size)
        print('\tTotal Time for job to complete: ', totalSeconds)
        print('\tTotal Job throughput: ', job_size / totalSeconds, "Mbps")
