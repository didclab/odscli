import click
import logging
import os
from odscli.sdk.measure.measure_carbon import traceroute, compute_carbon_per_ip, geo_locate_ips
from odscli.sdk.measure.measure_host_network import begin_measuring
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


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

@measure.command("host")
@click.option('--nic','--interface', required=True, help='The network interface to measure, the default is the interface with UP status')
@click.option('-K', '--kernel', 'measure_kernel', default=False, type=bool, help='Use if you wish to measure the kernel')
@click.option('-N', '--network', 'measure_network', default=False, type=bool, help='Use if you wish to measure the network interface')
@click.option('-U', '--udp', 'measure_udp', default=False, type=bool, help='Use if you wish to monitor UDP')
@click.option('-T', '--tcp', 'measure_tcp', default=False, type=bool, help='Use if you wish to monitor TCP')
@click.option('-S', '--std-out', 'disable_std_out', default=False, type=bool, help='Disable printing the results to standard output')
@click.option('-F','--file-path', 'file_path', default=os.path.join(os.path.expanduser("~"), '.config', 'pmeter_measure.txt'), type=click.Path(), help='Set the file path used to measure')
@click.option('-I','--interval', default='00:00:01', help='Set the time to run the measurement in the format HH:MM:SS')
@click.option('-M','--measurements', default=1, type=int, help='The max number of times to measure your system')
@click.option('-L','--length', default='10s', help='The amount of time to run for: 5w, 4d 3h, 2m, 1s are some examples of 5 weeks, 4 days, 3 hours, 2 min, 1 sec')
def host_measure(interface, measure_kernel, measure_network, measure_udp, measure_tcp, disable_std_out, file_path, interval, measurements, length):
    # Your measurement logic goes here
    click.echo(f"Measuring network activity on {interface}")
    click.echo(f"Measure Kernel: {measure_kernel}")
    click.echo(f"Measure Network: {measure_network}")
    click.echo(f"Measure UDP: {measure_udp}")
    click.echo(f"Measure TCP: {measure_tcp}")
    click.echo(f"Enable Std Out: {disable_std_out}")
    click.echo(f"File Path: {file_path}")
    click.echo(f"Interval: {interval}")
    click.echo(f"Measurements: {measurements}")
    click.echo(f"Length: {length}")
    begin_measuring(interface=interface, measure_kernel=measure_kernel, measure_network=measure_network,
                    measure_udp=measure_udp, measure_tcp=measure_tcp, print_to_std_out=disable_std_out, file_path=file_path,
                    interval=interval, measurement=measurements, length=length)


