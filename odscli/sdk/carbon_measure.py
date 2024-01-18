import click
import os
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr1
from scapy.config import conf

conf.use_pcap = True

import requests
import pandas as pd


@click.group('measure_cli')
@click.pass_context
def measure_cli():
    pass


@measure_cli.group('measure')
def measure():
    pass


@measure.command("carbon")
@click.option('--ip', default="", help="The IP address of the destination host", type=click.STRING)
@click.option('--max_hops', default=64, type=click.INT)
def carbon_measure(ip, max_hops):
    ip_list = traceroute(ip, max_hops)
    print(f"IP's to source {ip_list}")
    ip_df = geo_locate_ips(ip_list)
    compute_carbon_per_ip(ip_df)
    # pass


def traceroute(destination, max_hops):
    ip_list = []
    for ttl in range(1, max_hops + 1):
        packet = IP(dst=destination, ttl=ttl) / ICMP()
        reply = sr1(packet, verbose=0, timeout=1)
        if reply is None:
            break
        elif reply.src == destination:
            print(reply.src)
            ip_list.append(reply.src)
            break
        else:
            print(reply.src)
            ip_list.append(reply.src)
    return ip_list


def geo_locate_ips(ip_list):
    access_key = os.getenv("GEO_LOCATE_ACCESS_KEY")

    url = "http://api.ipstack.com/"
    params = {'access_key': access_key}
    json_list = []
    response_list = []
    for ip in ip_list:
        local_url = url + str(ip)
        r = requests.get(url=local_url, params=params)
        response_list.append(r)
        json_list.append(r.json())
    df = pd.DataFrame(json_list)
    return df


def compute_carbon_per_ip(ip_df):
    # ip_df = pd.read_json('location_to_ip.json')
    ip_df.dropna(inplace=True)
    ip_df.reset_index(drop=True, inplace=True)
    auth_token = os.getenv("ELECTRICITY_MAPS_AUTH_TOKEN")
    headers = {
        'auth-token': str(auth_token)
    }
    # Split the string into a list with one element
    resp_list = []
    carbon_ip_map = {}
    for idx, row in ip_df.iterrows():
        cur_lat = row['latitude']
        cur_long = row['longitude']
        cur_ip = row['ip']
        params = {'lon': cur_long, 'lat': cur_lat}
        resp = requests.get(url="https://api-access.electricitymaps.com/free-tier/carbon-intensity/latest",
                            params=params, headers=headers)
        carbon_data_json = resp.json()
        carbon_ip_map[cur_ip] = carbon_data_json['carbonIntensity']
        resp_list.append(resp)
    carbon_intensity_path_total = 0
    for ip in carbon_ip_map:
        carbon_intensity_path_total += carbon_ip_map[ip]
    avg_carbon_network_path = carbon_intensity_path_total / len(carbon_ip_map)
    print("Average Carbon cost for network path: ", avg_carbon_network_path)
    return avg_carbon_network_path
