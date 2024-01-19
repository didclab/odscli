import os
import datetime
from platform import system, platform
from statistics import mean
import requests
from psutil import net_connections, cpu_freq, net_io_counters, net_io_counters, net_if_stats, net_io_counters
from json import dumps
from multiprocessing import cpu_count
from tcp_latency import measure_latency
from pathlib import Path


class ODS_Metrics():

    def __init__(self):
        # kernel metrics
        self.interface = ""
        self.ods_user = ""
        self.active_core_count = 0
        self.cpu_frequency_max = 0.0
        self.cpu_frequency_current = 0.0
        self.cpu_frequency_min = 0.0
        self.energy_consumed = 0.0
        self.cpu_arch = ""
        # network metrics
        self.rtt = 0.0
        self.bandwidth = 0.0
        self.bandwidth_delay_product = 0.0
        self.packet_loss_rate = 0.0
        self.link_capacity = 0.0
        self.bytes_sent = 0.0
        self.bytes_recv = 0.0
        self.bytes_sent_delta = 0
        self.bytes_recv_delta = 0
        self.packets_sent = 0
        self.packets_recv = 0
        self.packets_sent_delta = 0
        self.packets_recv_delta = 0
        self.dropin = 0
        self.dropout = 0
        self.dropin_delta = 0
        self.dropout_delta = 0
        self.nic_speed = 0  # this is in mb=megabits
        self.nic_mtu = 0  # max transmission speed of nic
        # identifying properties
        self.start_time = ""
        self.end_time = ""
        self.count = 0
        self.latency = []

    def set_user(self, user_passed):
        user = os.getenv('ODS_USER', '')
        if len(user_passed) > 0:
            self.ods_user = user_passed
        else:
            self.ods_user = user

    def measure(self, interface='', measure_tcp=True, measure_udp=True, measure_kernel=True, measure_network=True,
                print_to_std_out=False, latency_host="http://google.com"):
        self.start_time = datetime.now().__str__()
        self.interface = interface
        if measure_kernel:
            self.measure_kernel()
        if measure_network:
            print('Getting metrics of: ' + interface)
            # we could take the average of all speeds that every socket experiences and thus get a rough estimate of bandwidth??
            self.measure_network(interface)
            self.measure_latency_rtt(latency_host)
        if measure_tcp:
            print('Measuring tcp')
            net_connections(kind="tcp")
        if measure_udp:
            print('Measuring udp')
            net_connections(kind="udp")
        self.end_time = datetime.now().__str__()
        if (print_to_std_out):
            print("\n", dumps(self.__dict__), "\n")
        # self.to_file()

    def measure_kernel(self):
        if system() != 'Darwin':
            freq = cpu_freq()
            self.cpu_frequency_max = freq[2]
            self.cpu_frequency_current = freq[0]
            self.cpu_frequency_min = freq[1]
            print(freq)
        self.cpu_arch = platform()
        self.active_core_count = cpu_count()

    def measure_latency_rtt(self, latency_host="http://google.com"):
        self.latency = mean(measure_latency(host="google.com"))  # in miliseconds and a list
        r = requests.get(latency_host)
        self.rtt = r.elapsed.microseconds / 1000
        print('Latency =', self.latency, " RTT=", self.rtt)
        print('LatencyType =', type(self.latency), " RTT Type=", type(self.rtt))

    def measure_network(self, interface):
        nic_counter_dic = net_io_counters(pernic=True, nowrap=True)
        if interface not in nic_counter_dic:
            raise Exception("The interface passed was not found on your system")
        interface_counter_tuple = nic_counter_dic[interface]
        self.bytes_sent = interface_counter_tuple[0]
        self.bytes_recv = interface_counter_tuple[1]
        self.packets_sent = interface_counter_tuple[2]
        self.packets_recv = interface_counter_tuple[3]
        self.errin = interface_counter_tuple[4]
        self.errout = interface_counter_tuple[5]
        self.dropin = interface_counter_tuple[6]
        self.dropout = interface_counter_tuple[7]
        sys_interfaces = net_if_stats()
        interface_stats = sys_interfaces[self.interface]
        self.nic_mtu = interface_stats[3]
        self.nic_speed = interface_stats[2]

    def get_system_interfaces(self):
        nic_counter_dic = net_io_counters(pernic=True, nowrap=True)
        return nic_counter_dic.keys()

    def to_file(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        j = dumps(self.__dict__)
        with open(file_path, "a+") as f:
            f.write(j + "\n")

    def do_deltas(self, old_metric):
        self.bytes_sent_delta = self.bytes_sent - old_metric.bytes_sent
        self.bytes_recv_delta = self.bytes_recv - old_metric.bytes_recv
        self.packets_sent_delta = self.packets_sent - old_metric.packets_sent
        self.packets_recv_delta = self.packets_recv - old_metric.packets_recv
        self.errin_delta = self.errin - old_metric.errin
        self.errout_delta = self.errout - old_metric.errout
        self.dropin_delta = self.dropin - old_metric.dropin
        self.dropout_delta = self.dropout - old_metric.dropout
