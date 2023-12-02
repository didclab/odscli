import pandas as pd
from datetime import datetime
import os

class Log:

    def visualize_job(self, batch_job_json, output_file=None):
        print(batch_job_json)
        job_params = batch_job_json['jobParameters']
        print("Job MetaData: ")
        job_size = int(batch_job_json['jobParameters']['jobSize'])
        job_size_gb = job_size / 1000000000  # convert to GB
        job_df = pd.DataFrame(columns=['jobId', 'jobSizeGb', 'job_seconds', 'startTime', 'endTime', "Mbps"])
        job_seconds = 0
        throughput = 0
        if 'sourceCredentialType' in job_params and 'destCredentialType' in job_params:
            print("SourceType: ", job_params['sourceCredentialType'], "----->", " DestinationType:", job_params['destCredentialType'], "\n")

        if 'concurrency' in job_params and 'pipelining' in job_params and 'parallelism' in job_params and 'chunkSize' in job_params:
            print("(Concurrency,Parallelism, Pipelining, ChunkSize) (", job_params['concurrency'], job_params['parallelism'], job_params["pipelining"], job_params['chunkSize'], ")")

        if 'startTime' in batch_job_json and 'endTime' in batch_job_json:
            if batch_job_json['endTime'] is not None:
                job_seconds = self.time_difference(batch_job_json['startTime'], batch_job_json['endTime'])
                job_size_mb = job_size / 1000000
                milliseconds = job_seconds * 1000  # this gives milliseconds
                throughput = (job_size_mb / milliseconds) * 1000
            one_row = [batch_job_json['id'], job_size_gb, job_seconds, batch_job_json['startTime'],
                       batch_job_json['endTime'], throughput]
            job_df.loc[len(job_df.index)] = one_row
        print(job_df)
        print("\n")
        if output_file is not None:
            output_file +='.csv'
            job_df.to_csv(output_file, index=False)
            print("Output saved to", output_file)



    def visualize_steps(self, batch_job_json, output_file=None):
        print("File MetaData: ")
        file_steps_df = pd.DataFrame.from_records(batch_job_json['batchSteps'])
        job_params = batch_job_json['jobParameters']
        if len(file_steps_df) > 1:
            columns_to_select = ['step_name', 'jobInstanceId', 'startTime', 'endTime', 'status', 'exitMessage']
            if 'endTime' not in file_steps_df:
                file_steps_df['endTime'] = None
            file_steps_df = file_steps_df[columns_to_select]
            file_size_list_in_order = []
            # Construct file size in df from job params
            for step_name in file_steps_df['step_name']:
                file_info = str(job_params[step_name])
                size_str = file_info.split(",")[2]
                file_size = size_str.split("=")[1]
                file_size_list_in_order.append(int(file_size))
            file_steps_df.insert(loc=2, column="fileSize", value=file_size_list_in_order)

        # compute throughput per step
            throughput_list_in_order = []
            for idx, row in file_steps_df.iterrows():
                file_size = row['fileSize']
                file_size_mb = 0.000008 * file_size
                start_time = row['startTime']
                if 'endTime' not in row:
                    row['endTime'] = None
                end_time = row['endTime']

                if Log.check_if_job_done(row['status']):
                    seconds = self.time_difference(start_time, end_time)
                    milliseconds = seconds * 1000  # this gives milliseconds
                    throughput = (file_size_mb / milliseconds) * 1000

                else:
                    throughput = 0.0
                throughput_list_in_order.append(throughput)
            file_steps_df.insert(loc=2, column="Mbps", value=throughput_list_in_order)
        print(file_steps_df)

        if output_file is not None:
            output_file +='.csv'
            with open(output_file, 'a') as f:
                file_steps_df.to_csv(f, index=False, header=True)
            print("Output appended to", output_file)

    def time_difference(self, start_time, end_time):
        print(start_time, end_time)
        format = '%Y-%m-%dT%H:%M:%S.%f%z'
        # start_date_time_obj = datetime.strptime(start_time, format)
        # end_date_time_obj = datetime.strptime(end_time, format)
        start_date_time_obj = datetime.fromisoformat(str(start_time).split("+")[0])
        end_date_time_obj = datetime.fromisoformat(str(end_time).split("+")[0])
        tdelta = end_date_time_obj - start_date_time_obj
        return tdelta.total_seconds()

    def check_if_job_done(status):
        if status == "COMPLETED" or status == "FAILED" or status == "ABANDONED" or status == "STOPPED":
            return True
        else:
            return False

    def has_job_started(batch_job_json):
        if 'endTime' in batch_job_json:
            return True
        if 'startTime' in batch_job_json:
            return True
        else:
            return False

    def visualize_influx_data(self, job_influx_json, output_file):
        # pd.DataFrame(columns=['jobId', 'concurrency', 'parallelism', 'pipelining', 'read'])

        print("\nInflux Transfer Data: ")
        cols_to_use = ['sourceRtt', 'destinationRtt', 'readThroughput', 'writeThroughput', 'bytesRead', 'bytesWritten', 'networkInterface', ]
        influx_df = pd.DataFrame.from_records(job_influx_json)
        influx_df = pd.concat([influx_df])
        # print(influx_df.shape)
        # print(influx_df.columns)
        select_cols = []
        for col in cols_to_use:
            if col in influx_df.columns:
                select_cols.append(col)
            std_out_df = influx_df[select_cols]
        print("\n",std_out_df)
        if output_file is not None:
            #if we are saving the data to file then make sure the directories exist.
            directory_path = os.path.dirname(output_file)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

            with open(output_file, 'a') as f:
                std_out_df.to_csv(f, index=False, header=True)
            print("Output appended to", output_file)
