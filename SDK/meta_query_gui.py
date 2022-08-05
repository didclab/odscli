import pandas as pd
from SDK.meta_query import MetaQueryAPI
from tabulate import tabulate
from datetime import datetime


class QueryGui:

    def __init__(self):
        self.df = pd.DataFrame()
        self.mq = MetaQueryAPI()

    def monitor(self, job_ids_to_monitor, delta_t):
        print('monitoring ', job_ids_to_monitor, delta_t)

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
                job_batch_json = self.mq.query_range_cdb(start_date_time=self.parse_time(start_date), end_date_time=self.parse_time(end_date))
                job_influx_json = self.mq.query_range_influx(start_date=self.parse_time(start_date), end_date=self.parse_time(end_date))
            elif all is True:
                job_batch_json = self.mq.all_user_stats_cdb()
                job_influx_json = self.mq.all_user_measurements_influx()
        elif cdb_only is True:
            if job_id is not None and int(job_id) > 0:
                job_batch_json = self.mq.query_job_id_cdb(job_id)
            elif start_date is not None and end_date is not None:
                job_batch_json = self.mq.query_range_cdb(start_date_time=self.parse_time(start_date), end_date_time=self.parse_time(end_date))
            elif all is True:
                job_batch_json = self.mq.all_user_stats_cdb()
        elif influx_only:
            if job_id is not None and int(job_id) > 0:
                job_influx_json = self.mq.query_job_id_influx(job_id)
            elif start_date is not None and end_date is not None:
                job_influx_json = self.mq.query_range_influx(start_date=self.parse_time(start_date), end_date=self.parse_time(end_date))
            elif all is True:
                job_influx_json = self.mq.all_user_measurements_influx()

    def parse_time(self, time):
        if time is None:
            return None
        if isinstance(time, datetime):
            return time
        print('User input: ',time)
        date_time_obj = datetime.strptime(time, "%Y-%m-%dT%H:%M")
        print('datetime obj: ', date_time_obj)
        res = date_time_obj.utcnow().isoformat()
        print('datetime obj w/o +:', res)
        if not isinstance(time, datetime):
            print("Invalid date format please do yyyy-mm-ddTHH:MM for submitting time format for start_date and end_date")
        return res
