import configs
import csv
from scipy import stats
import numpy as np
from pathlib import Path
import math

from utils import get_avg_without_outlier, get_std_without_outlier


def add_csv_headers_for_application(csv_writer):
    header = []
    ################### Experiment Info #########################
    header.append('device')
    header.append('ip')
    header.append('application')
    header.append('fault')
    header.append('config')
    #############################################################

    ################# AVG Results Headers ###################
    header.append('avg_response_time')
    header.append('avg_compute_time')
    header.append('avg_transmission_time')
    header.append('average_cpu_utilization')
    header.append('average_memory_utilization')
    header.append('average_disk_utilization')
    header.append('average_network_utilization')
    header.append('average_power_consumption')

    ################# STD Results Headers ###################
    header.append('std_response_time')
    header.append('std_compute_time')
    header.append('std_transmission_time')
    header.append('std_cpu_utilization')
    header.append('std_memory_utilization')
    header.append('std_disk_utilization')
    header.append('std_network_utilization')
    header.append('std_power_consumption')
    csv_writer.writerow(header)


def add_csv_row_for_application(csv_writer, device, ip, application, fault, config,
                                response_times, compute_times, transmission_times, cpu_utils,
                                mem_utils, disk_utils, net_utils, power_cons):
    row = []
    ################### Experiment Info #########################
    row.append(device)
    row.append(ip)
    row.append(application)
    row.append(fault)
    row.append(config)
    #############################################################

    ################# AVG Results Headers ###################
    row.append("{0:.1f}".format(get_avg_without_outlier(response_times)))
    row.append("{0:.1f}".format(get_avg_without_outlier(compute_times)))
    row.append("{0:.1f}".format(get_avg_without_outlier(transmission_times)))
    row.append("{0:.1f}".format(get_avg_without_outlier(cpu_utils)))
    row.append("{0:.1f}".format(get_avg_without_outlier(mem_utils)))
    row.append("{0:.1f}".format(get_avg_without_outlier(disk_utils)))
    row.append("{0:.1f}".format(get_avg_without_outlier(net_utils)))
    row.append("{0:.1f}".format(get_avg_without_outlier(power_cons)))

    ################# STD Results Headers ###################
    row.append("{0:.1f}".format(get_std_without_outlier(response_times)))
    row.append("{0:.1f}".format(get_std_without_outlier(compute_times)))
    row.append("{0:.1f}".format(get_std_without_outlier(transmission_times)))
    row.append("{0:.1f}".format(get_std_without_outlier(cpu_utils)))
    row.append("{0:.1f}".format(get_std_without_outlier(mem_utils)))
    row.append("{0:.1f}".format(get_std_without_outlier(disk_utils)))
    row.append("{0:.1f}".format(get_std_without_outlier(net_utils)))
    row.append("{0:.1f}".format(get_std_without_outlier(power_cons)))
    csv_writer.writerow(row)


def analyze_result_file(filename):
    latency_file_rows = []
    response_times = []
    compute_times = []
    transmission_times = []
    cpu_utilization = []
    mem_utilization = []
    disk_utilization = []
    net_utilization = []
    power_consumption = []

    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        row_number = 1
        for row in csvreader:
            latency_file_rows.append(row)
            response_times.append(int(row[5]))
            compute_times.append(int(row[6]))
            transmission_times.append(int(row[7]))
            cpu_utilization.append(float(row[8]))
            mem_utilization.append(float(row[9]))
            disk_utilization.append(float(row[10]))
            net_utilization.append(float(row[11]))
            power_consumption.append(float(row[12]))
            row_number += 1

    return response_times, compute_times, transmission_times, cpu_utilization, mem_utilization, \
        disk_utilization, net_utilization, power_consumption


def analyze_result_for_application(application, edge_device_ip):
    with open('results/summaries/raspberrypi-' + application + '.csv', 'w', encoding='UTF8', newline='') as csv_output:
        writer = csv.writer(csv_output)
        add_csv_headers_for_application(writer)

        result_nofault_filename = 'results/raspberrypi/' + application + '-no-fault.csv'
        response_times, compute_times, transmission_times, cpu_utilization, mem_utilization, \
            disk_utilization, net_utilization, power_consumption = analyze_result_file(result_nofault_filename)
        add_csv_row_for_application(writer, 'raspberrypi', edge_device_ip, application, 'no', 'fault',
                                    response_times, compute_times, transmission_times, cpu_utilization, mem_utilization,
                                    disk_utilization, net_utilization, power_consumption)

        # Experiments with Fault Injection
        for fault in configs.FAULTS:
            for fault_config in fault.fault_config:
                result_fault_filename = 'results/raspberrypi/' + application + \
                                        '{0}-{1}'.format(fault.abbreviation, fault_config) + '.csv'
                if Path(result_fault_filename).is_file():
                    response_times, compute_times, transmission_times, cpu_utilization, mem_utilization, \
                        disk_utilization, net_utilization, power_consumption = analyze_result_file(
                        result_fault_filename)
                    add_csv_row_for_application(writer, 'raspberrypi', edge_device_ip, application,
                                                fault.abbreviation, fault_config, response_times, compute_times,
                                                transmission_times, cpu_utilization, mem_utilization,
                                                disk_utilization, net_utilization, power_consumption)
