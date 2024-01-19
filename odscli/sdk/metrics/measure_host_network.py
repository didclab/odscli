import time

from datetime import datetime, timedelta

from odscli.sdk.measure.metrics_pojo import ODS_Metrics


def begin_measuring(file_path, interface, measure_tcp=True, measure_udp=True,
                    measure_kernel=True, measure_network=True, print_to_std_out=False, interval=1,
                    latency_host="http://google.com", measurement=1, length="0s", user=""):
    metric = ODS_Metrics()
    metric.set_user(user)
    interface_list = []
    if interface == "all":
        for inter_name in metric.get_system_interfaces():
            interface_list.append(inter_name)
    else:
        interface_list.append(interface)
    if measurement == 0:
        print("Measuring by using the duration specified with interval")
        measure_using_length(interface_list=interface_list, metric=metric, file_path=file_path, measure_tcp=measure_tcp, measure_udp=measure_udp,
                             measure_kernel=measure_kernel, measure_network=measure_network,
                             print_to_std_out=print_to_std_out, latency_host=latency_host, interval=interval,
                             length=length)
    if length == '0':
        print("Measuring by using the number of measurments to perform with interval")
        measure_using_measurements(interface_list=interface_list, metric=metric, file_path=file_path, measure_tcp=measure_tcp,
                                   measure_udp=measure_udp, measure_kernel=measure_kernel,
                                   measure_network=measure_network, print_to_std_out=print_to_std_out,
                                   latency_host=latency_host, interval=interval, measurement=measurement)
    else:
        measurements_counter = 0
        end_date = convert_to_endate(length)
        current_date = datetime.now()
        while current_date < end_date and measurements_counter < measurement:
            print("Current date= ", str(current_date), "is less than end date=", str(end_date), " is =",
                  current_date < end_date)
            print("currentMeasurement is less than the max measurements", measurements_counter < measurement)
            for intr_name in interface_list:
                metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                               latency_host)
                metric.to_file(file_path)
            current_date = datetime.now()
            measurements_counter += 1
            time.sleep(interval)


def measure_using_length(interface_list, metric, file_path, measure_tcp=True,
                         measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False,
                         latency_host="http://google.com", interval=1, length="0s"):
    end_date = convert_to_endate(length)
    current_date = datetime.now()
    while (current_date < end_date):
        print("Current date is less than end date=", current_date < end_date)
        metric.measure_latency_rtt(latency_host)
        for intr_name in interface_list:
            metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                           latency_host)
            metric.to_file(file_path=file_path)
        current_date = datetime.now()
        time.sleep(interval)


def measure_using_measurements(interface_list, metric, file_path, measure_tcp=True,
                               measure_udp=True, measure_kernel=True, measure_network=True, print_to_std_out=False,
                               latency_host="http://google.com", interval=1, measurement=1):
    for i in range(0, measurement):
        metric.measure_latency_rtt(latency_host)
        print("measurement: ", i)
        for intr_name in interface_list:
            metric.measure(intr_name, measure_tcp, measure_udp, measure_kernel, measure_network, print_to_std_out,
                           latency_host)
            metric.to_file(file_path=file_path)
        time.sleep(interval)


def convert_to_endate(length):
    end_date = datetime.now()
    num = int(length[:-1])
    if "s" in length:
        end_date += timedelta(seconds=num)
    if "m" in length:
        end_date += timedelta(minutes=num)
    if "d" in length:
        end_date += timedelta(days=num)
    if "w" in length:
        end_date += timedelta(weeks=num)
    if "h" in length:
        end_date += timedelta(hours=num)
    return end_date
