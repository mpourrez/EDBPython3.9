import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import time
import pytz
import math
import utils
from utils import get_avg_without_outlier, get_std_without_outlier


class AppFaultStatistics:
    def __init__(self, app, fault):
        super().__init__()
        self.app = app
        self.fault = fault

        # Fault Injection Times
        self.fault_start_times, self.fault_stop_times = None, None
        # CPU Utilizations
        self.cpu_datetimes, self.user_cpu_utilization, self.sys_cpu_utilization, self.total_cpu_utilization = None, None, None, None
        # CPU Temperatures
        self.cpu_temp_datetimes, self.cpu_temperatures = None, None
        # Latencies
        self.request_datetimes, self.response_datetimes, self.compute_times, self.transmission_times = None, None, None, None
        # Memory Utilizations
        self.mem_datetimes, self.mem_utilization = None, None
        # Network Utilizations
        self.net_datetimes, self.net_utilizations, self.net_receive_rates, self.net_transmit_rates = None, None, None, None
        # Disk Utilizations
        self.io_datetimes, self.disk_utilization = None, None
        self.read_all_saved_statistics()

    def read_all_saved_statistics(self):
        self.get_fault_injection_times()
        self.get_cpu_utilization()
        self.get_cpu_temperatures()
        self.get_latencies()
        self.get_iostat()
        self.get_network_statistics()
        self.get_memory_utilization()

    def get_resource_datetimes(self, resource):
        resource_datetime = None
        if resource == 'CPU':
            resource_datetime = self.cpu_datetimes
        elif resource == 'MEM':
            resource_datetime = self.mem_datetimes
        elif resource == 'NET':
            resource_datetime = self.net_datetimes
        elif resource == 'DISK':
            resource_datetime = self.io_datetimes
        elif resource == 'LATENCY':
            resource_datetime = self.request_datetimes
        else:
            resource_datetime = self.cpu_temp_datetimes
        return resource_datetime

    def get_resource_values(self, resource, rtype):
        values = None
        if resource == 'CPU' and rtype=='SYS':
            values = self.sys_cpu_utilization
        elif resource == 'CPU' and rtype == 'USR':
            values = self.user_cpu_utilization
        elif resource == 'CPU' and rtype == 'UTIL':
            values = self.total_cpu_utilization
        elif resource == 'MEM':
            values = self.mem_utilization
        elif resource == 'NET' and rtype == 'REC':
            values = self.net_receive_rates
        elif resource == 'NET' and rtype == 'TRA':
            values = self.net_transmit_rates
        elif resource == 'NET' and rtype == 'UTIL':
            values = self.net_utilizations
        elif resource == 'DISK':
            values = self.disk_utilization
        elif resource == 'LATENCY' and rtype=='COM-TIME':
            values = self.compute_times
        elif resource == 'LATENCY' and rtype=='TRA-TIME':
            values = self.transmission_times
        else:
            values = self.cpu_temperatures
        return values

    def get_resource_metric(self, resource, rtype):
        metric = None
        if resource == 'NET' and rtype == 'REC':
            metric = 'kB/s'
        elif resource == 'NET' and rtype == 'TRA':
            metric = 'kB/s'
        elif resource == 'LATENCY' and rtype == 'COM-TIME':
            metric = 'ms'
        elif resource == 'LATENCY' and rtype == 'TRA-TIME':
            metric = 'ms'
        else:
            metric = '%'
        return metric

    def get_faulty_values(self, resource, rtype):
        resource_datetime = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetime, self.fault_start_times)
        _, resource_faulty_values = get_fault_free_faulty_values(resource_values, fault_start_indices, fault_end_indices)
        return resource_faulty_values
    def get_fault_free_values(self, resource, rtype):
        resource_datetime = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetime, self.fault_start_times)
        resource_fault_free_values, _ = get_fault_free_faulty_values(resource_values, fault_start_indices, fault_end_indices)
        return resource_fault_free_values
    def get_fault_injection_times(self):
        fault_injection_times = pd.read_csv(
            'results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-FaultInjection.csv',
            delimiter=',')
        fault_start_times_cl = fault_injection_times['fault_injection_start_time']
        fault_stop_times_cl = fault_injection_times['fault_injection_stop_time']

        self.fault_start_times = []
        self.fault_stop_times = []

        for start_t, stop_t in zip(fault_start_times_cl, fault_stop_times_cl):
            fault_start_time = get_datetime_from_timestamp(self.app, self.fault, start_t)
            fault_end_time = get_datetime_from_timestamp(self.app, self.fault, stop_t)
            self.fault_start_times.append(fault_start_time)
            self.fault_stop_times.append(fault_end_time)

    #############################################
    #########     CPU Utilization    ############
    #############################################
    def get_cpu_utilization(self):
        date = '2023-04-17 '
        if self.app == 'DD' or (self.app == 'SORT' and self.fault == 'CPU-80') or (self.app == 'SORT' and self.fault == 'IO-100') or (
                self.app == 'SORT' and self.fault == 'PF-0') or (self.app == 'SORT' and self.fault == 'CCHE-0') or (
                self.app == 'SORT' and self.fault == 'CTXS-10000') or (self.app == 'FPO-SIN' and self.fault == 'MEM-80%') or (
                self.app == 'IPERF'):
            date = '2023-04-18 '
        elif self.app == 'IPERF':
            date = '2023-04-20 '
        elif self.app == 'IP' or self.app == 'SA' or self.app == 'OD-CPU':
            date = '2023-04-21 '


        cpu_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-CPU.txt',
                             delimiter='\s+', skiprows=2)
        cpu_times = cpu_df.iloc[:, 0]
        self.cpu_datetimes = []
        for t in cpu_times:
            cpu_datetime = datetime.datetime.strptime(date + t + ' PM', '%Y-%m-%d %I:%M:%S %p')
            self.cpu_datetimes.append(cpu_datetime)
        self.user_cpu_utilization = cpu_df['%usr']
        self.sys_cpu_utilization = cpu_df['%sys']
        self.total_cpu_utilization = 100 - cpu_df['%idle']

    #############################################
    #########     CPU Temperatures    ###########
    #############################################
    def get_cpu_temperatures(self):
        cpu_temp_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-TEMP.txt', delimiter=',')
        cpu_temp_times = cpu_temp_df['Timestamp_ms']
        self.cpu_temp_datetimes = []
        for t in cpu_temp_times:
            self.cpu_temp_datetimes.append(get_datetime_from_timestamp(self.app, self.fault, t))
        self.cpu_temperatures = cpu_temp_df['CPU_Temp']


    #############################################
    #########     Latencies    ##################
    #############################################
    def get_latencies(self):
        latencies_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-Latency.csv', delimiter=',')
        request_times = latencies_df['request_received_time_ms']
        response_times = latencies_df['response_time_ms']
        self.compute_times = latencies_df['compute_time']
        self.transmission_times = latencies_df['transmission_time']

        self.request_datetimes = []
        self.response_datetimes = []

        for req, res in zip(request_times, response_times):
            self.request_datetimes.append(get_datetime_from_timestamp(self.app, self.fault, req))
            self.response_datetimes.append(get_datetime_from_timestamp(self.app, self.fault, res))

    #############################################
    #########     Disk Utilization    ###########
    #############################################
    def get_iostat(self):
        date = '2023-04-17 '
        if self.app == 'DD' or (self.app == 'SORT' and self.fault == 'CPU-80') or (
                self.app == 'SORT' and self.fault == 'IO-100') or (
                self.app == 'SORT' and self.fault == 'PF-0') or (self.app == 'SORT' and self.fault == 'CCHE-0') or (
                self.app == 'SORT' and self.fault == 'CTXS-10000') or (
                self.app == 'FPO-SIN' and self.fault == 'MEM-80%') or (
                self.app == 'IPERF'):
            date = '2023-04-18 '
        elif self.app == 'IPERF':
            date = '2023-04-20 '
        elif self.app == 'IP' or self.app == 'SA' or self.app == 'OD-CPU':
            date = '2023-04-21 '

        io_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-IO.txt', delimiter='\s+',
                            skiprows=3)
        self.io_datetimes = []
        self.disk_utilization = []  # %util
        writes_ps = []  # w/s
        write_kilobytes = []  # wkB/s
        write_wait_times = []  # w_await
        first = True
        for i in range(len(io_df)):
            if io_df.iloc[:, 0][i] == '04/16/2023' or io_df.iloc[:, 0][i] == '04/17/2023' or \
                    io_df.iloc[:, 0][i] == '04/18/2023' or io_df.iloc[:, 0][i] == '04/20/2023' or io_df.iloc[:, 0][i] == '04/21/2023':
                io_time = io_df.iloc[:, 1][i]
                io_datetime = datetime.datetime.strptime(date + io_time + ' PM', '%Y-%m-%d %I:%M:%S %p')
                if first:
                    first_missing_date = io_datetime.replace(minute=(io_datetime.minute - 1))
                    self.io_datetimes.append(first_missing_date)
                    first = False
                self.io_datetimes.append(io_datetime)
            elif io_df.iloc[:, 0][i] == 'mmcblk0':
                self.disk_utilization.append(float(io_df.iloc[:, 22][i]))


    #############################################
    #########     NEtwork Utilizations    #######
    #############################################
    def get_network_statistics(self):
        date = '2023-04-17 '
        if self.app == 'DD' or (self.app == 'SORT' and self.fault == 'CPU-80') or (
                self.app == 'SORT' and self.fault == 'IO-100') or (
                self.app == 'SORT' and self.fault == 'PF-0') or (self.app == 'SORT' and self.fault == 'CCHE-0') or (
                self.app == 'SORT' and self.fault == 'CTXS-10000') or (
                self.app == 'FPO-SIN' and self.fault == 'MEM-80%') or (
                self.app == 'IPERF'):
            date = '2023-04-18 '
        elif self.app == 'IPERF':
            date = '2023-04-20 '
        elif self.app == 'IP' or self.app == 'SA' or self.app == 'OD-CPU':
            date = '2023-04-21 '

        net_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-NET.txt', delimiter='\s+',
                             skiprows=2)
        self.net_datetimes = []
        self.net_utilizations = []  # %ifutil
        self.net_receive_rates = []  # rxkB/s The number of kilobytes received per second.
        self.net_transmit_rates = []  # txkB/s: The number of kilobytes transmitted per second

        for i in range(len(net_df)):
            if self.app == 'IP' or self.app == 'SA' or self.app == 'OD-CPU':
                if net_df.iloc[:, 2][i] == 'wlan0':
                    net_time = net_df.iloc[:, 0][i]
                    net_datetime = datetime.datetime.strptime(date + net_time + ' PM', '%Y-%m-%d %I:%M:%S %p')
                    self.net_datetimes.append(net_datetime)

                    self.net_utilizations.append(float(net_df.iloc[:, 10][i]))
                    self.net_receive_rates.append(float(net_df.iloc[:, 5][i]))
                    self.net_transmit_rates.append(float(net_df.iloc[:, 6][i]))
            else:
                if net_df.iloc[:, 2][i] == 'lo':
                    net_time = net_df.iloc[:, 0][i]
                    net_datetime = datetime.datetime.strptime(date + net_time + ' PM', '%Y-%m-%d %I:%M:%S %p')
                    self.net_datetimes.append(net_datetime)

                    self.net_utilizations.append(float(net_df.iloc[:, 10][i]))
                    self.net_receive_rates.append(float(net_df.iloc[:, 5][i]))
                    self.net_transmit_rates.append(float(net_df.iloc[:, 6][i]))

        if self.app=='IPERF':
            index_of_zero = 0
            for i, val in enumerate(self.net_receive_rates[1:], start=1):
                if all(x == 0.0 for x in self.net_receive_rates[i:]):
                    index_of_zero = i
                    break
            # index_of_zero = net_float_receive_rates.index(19291.64)
            print(index_of_zero)
            self.net_utilizations = self.net_utilizations[:index_of_zero]
            self.net_receive_rates = self.net_receive_rates[:index_of_zero]
            self.net_transmit_rates = self.net_transmit_rates[:index_of_zero]
            self.net_datetimes = self.net_datetimes[:index_of_zero]

    #############################################
    #########     Memory Utilizations    ########
    #############################################
    def get_memory_utilization(self):
        date = '2023-04-17 '
        if self.app == 'DD' or (self.app == 'SORT' and self.fault == 'CPU-80') or (
                self.app == 'SORT' and self.fault == 'IO-100') or (
                self.app == 'SORT' and self.fault == 'PF-0') or (self.app == 'SORT' and self.fault == 'CCHE-0') or (
                self.app == 'SORT' and self.fault == 'CTXS-10000') or (
                self.app == 'FPO-SIN' and self.fault == 'MEM-80%') or (
                self.app == 'IPERF'):
            date = '2023-04-18 '
        elif self.app == 'IPERF':
            date = '2023-04-20 '
        elif self.app == 'IP' or self.app == 'SA' or self.app == 'OD-CPU':
            date = '2023-04-21 '
        mem_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-MEM.txt',
                             delimiter='\s+', skiprows=2)
        mem_times = mem_df.iloc[:, 0]
        self.mem_datetimes = []
        first = True
        for t in mem_times:
            mem_datetime = datetime.datetime.strptime(date + t + ' PM', '%Y-%m-%d %I:%M:%S %p')
            self.mem_datetimes.append(mem_datetime)
        self.mem_utilization = mem_df['%memused']
        self.mem_utilization = self.mem_utilization[: len(self.mem_utilization) - 1]
        self.mem_datetimes = self.mem_datetimes[:len(self.mem_datetimes) - 1]


    ######################################################################################################################
    #################################     END: Reading Files      ########################################################
    ######################################################################################################################

    def plot_resource(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes, self.fault_start_times)
        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label='memused')
        if show_injection_times:
            for start in fault_start_indices:
                axs.axvline(x=resource_datetimes[start], color='r')
            for end in fault_end_indices:
                axs.axvline(x=resource_datetimes[end], color='b')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource+'-'+ rtype + ' ('+resource_metric+')', fontsize=16, fontweight='bold')
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource+'-'+ rtype+' Utilization Plot for App: '+self.app + ' - Fault: ' + self.fault, fontsize=16, fontweight='bold')
        plt.show()

    def jitter_faulty_fault_free(self, resource, rtype, is_faulty):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes,
                                                                                 self.fault_start_times)
        faulty_jitters = []
        fault_free_jitters = []
        start_ind = 0
        for fault_start, fault_end in zip(fault_start_indices, fault_end_indices):
            fault_free_values = resource_values[start_ind:fault_start]
            faulty_values = resource_values[fault_start:fault_end]

            faulty_jitters.append(jitter(faulty_values))
            print(jitter(faulty_values))
            fault_free_jitters.append(jitter(fault_free_values))
            start_ind = fault_end + 1

        fault_free_values = resource_values[start_ind:len(resource_datetimes) - 85]
        fault_free_jitters.append(jitter(fault_free_values))

        average_fault_free_jitter = sum(fault_free_jitters)/len(fault_free_jitters)
        average_faulty_jitter = sum(faulty_jitters)/len(faulty_jitters)

        if is_faulty:
            print("faulty avg: {0}".format(average_faulty_jitter))
            return average_faulty_jitter
        print("fault free avg: {0}".format(average_fault_free_jitter))
        return average_fault_free_jitter

    def plot_resource(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes, self.fault_start_times)
        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label='memused')
        if show_injection_times:
            for start in fault_start_indices:
                axs.axvline(x=resource_datetimes[start], color='r')
            for end in fault_end_indices:
                axs.axvline(x=resource_datetimes[end], color='b')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource+'-'+ rtype + ' ('+resource_metric+')', fontsize=16, fontweight='bold')
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource+'-'+ rtype+' Utilization Plot for App: '+self.app + ' - Fault: ' + self.fault, fontsize=16, fontweight='bold')
        plt.show()

    def plot_resource_with_residual(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes, self.fault_start_times)
        print(self.fault_start_times)
        print(resource_datetimes)

        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label=resource+'-'+rtype)

        residual_means = []
        residual_jitters = []
        residual_dates = []
        if show_injection_times:
            start_ind = 0
            for fault_start, fault_end in zip(fault_start_indices, fault_end_indices):
                axs.axvline(x=resource_datetimes[fault_start], color='r')
                axs.axvline(x=resource_datetimes[fault_end], color='b')

                fault_free_middle_date = resource_datetimes[start_ind] + (resource_datetimes[fault_start] - resource_datetimes[start_ind]) / 2
                faulty_middle_date = resource_datetimes[fault_start] + (resource_datetimes[fault_end] - resource_datetimes[fault_start]) / 2
                fault_free_values = resource_values[start_ind:fault_start]
                faulty_values = resource_values[fault_start:fault_end]

                residual_dates.append(fault_free_middle_date)
                residual_dates.append(faulty_middle_date)
                residual_means.append(sum(fault_free_values)/len(fault_free_values))
                residual_means.append(sum(faulty_values)/len(faulty_values))
                residual_jitters.append(jitter(fault_free_values))
                residual_jitters.append(jitter(faulty_values))
                start_ind = fault_end + 1

            extra_end = 85
            if resource =='NET':
                extra_end = 1

            fault_free_middle_date = resource_datetimes[len(resource_datetimes)-extra_end] + (
                        resource_datetimes[len(resource_datetimes)-extra_end] - resource_datetimes[start_ind]) / 2
            fault_free_values = resource_values[start_ind:len(resource_datetimes)-extra_end]
            residual_dates.append(fault_free_middle_date)
            residual_means.append(sum(fault_free_values) / len(fault_free_values))
            residual_jitters.append(jitter(fault_free_values))

        axs.plot(residual_dates, residual_means, label='residual-mean')
        axs.plot(residual_dates, residual_jitters, label='residual-jitter')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource+'-'+ rtype + ' ('+resource_metric+')', fontsize=16, fontweight='bold')
        # axs.legends()
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource+'-'+ rtype+' Utilization Plot for App: '+self.app + ' - Fault: ' + self.fault, fontsize=16, fontweight='bold')
        plt.show()


def normalized_jitter(values):
    # Normalize the values between 0 and 100
    min_value = min(values)
    max_value = max(values)
    normalized = [(x - min_value) / (max_value - min_value) * 100 for x in values]

    # Calculate the standard deviation of the normalized list
    mean_normalized = np.mean(normalized)
    std_normalized = np.std(normalized)
    return std_normalized

def jitter(values):
    n = len(values)
    if n <= 1:
        return 0.0
    mean = sum(values) / float(n)
    variance = sum((x - mean) ** 2 for x in values) / float(n - 1)
    return math.sqrt(variance)


def calculate_average_jitter_fault_free(values, fault_injection_times, fault_duration):
    jitter_sum = 0
    start_index = 1
    for i in range(len(fault_injection_times)):
        fault_start_time = fault_injection_times[i]
        value_on_fault = values[start_index:fault_start_time]
        jitter_sum += jitter(value_on_fault)
        start_index = fault_start_time + fault_duration
    return jitter_sum / len(fault_injection_times)


def calculate_average_jitter_on_faults(values, fault_injection_times, fault_duration):
    jitter_sum = 0
    for i in range(len(fault_injection_times)):
        fault_start_time = fault_injection_times[i]
        value_on_fault = values[fault_start_time:fault_start_time + fault_duration]
        jitter_sum += jitter(value_on_fault)
    return jitter_sum / len(fault_injection_times)


def get_datetime_from_timestamp(app, fault, timestamp):
    fault_start_time = datetime.datetime.fromtimestamp(timestamp / 1000)
    new_hour = fault_start_time.hour - 3
    if new_hour < 0:
        new_hour += 24
    fault_start_time_updated = fault_start_time.replace(hour=new_hour)
    if app == 'DD' or (app == 'SORT' and fault == 'CPU-80') or (app == 'SORT' and fault == 'IO-100') or (
            app == 'SORT' and fault == 'PF-0') or (app == 'SORT' and fault == 'CCHE-0') or (
            app == 'SORT' and fault == 'CTXS-10000') or (app == 'FPO-SIN' and fault == 'MEM-80%') or (app=='IPERF'):
        fault_start_time_updated = fault_start_time_updated.replace(year=2023, month=4, day=18)
        fault_start_time_updated = fault_start_time_updated.replace(hour=(fault_start_time_updated.hour+12))
    elif app=='IPERF':
        fault_start_time_updated = fault_start_time_updated.replace(year=2023, month=4, day=20)
        fault_start_time_updated = fault_start_time_updated.replace(hour=(fault_start_time_updated.hour+12))
    elif app=='IP' or app=='SA':
        fault_start_time_updated = fault_start_time_updated.replace(year=2023, month=4, day=21)
        fault_start_time_updated = fault_start_time_updated.replace(hour=(fault_start_time_updated.hour+12))
    elif app=='OD-CPU':
        fault_start_time_updated = fault_start_time_updated.replace(year=2023, month=4, day=21)
    else:
        fault_start_time_updated = fault_start_time_updated.replace(year=2023, month=4, day=17)
    return fault_start_time_updated


def find_fault_injection_indices_on_utilizations(utilization_times, fault_injection_times):
    index = 0
    fault_index = 0

    fault_injection_indices = []
    while index< len(utilization_times):
        if fault_index >= len(fault_injection_times):
            break
        if fault_injection_times[fault_index] < utilization_times[index]:
            fault_injection_indices.append(index)
            fault_index += 1
        index += 1

    return fault_injection_indices

def get_fault_free_faulty_values(values, fault_start_indices, fault_end_indices):
    index = 0
    fault_free_values = []
    faulty_values = []
    for i in range(len(values)):
        if index>=len(fault_start_indices) or i<fault_start_indices[index] and i<fault_end_indices[index]:
            fault_free_values.append(values[i])
        elif i>=fault_start_indices[index] and i>=fault_end_indices[index] and index<len(fault_start_indices):
            index += 1
            faulty_values.append(values[i])
        else:
            faulty_values.append(values[i])
    return fault_free_values, faulty_values


def extract_fault_start_end_indices(resource_datetimes, fault_start_times):
    resource_fault_start_indices = find_fault_injection_indices_on_utilizations(resource_datetimes, fault_start_times)
    resource_fault_end_datetimes = [dt + datetime.timedelta(seconds=30) for dt in fault_start_times]
    resource_fault_end_indices = find_fault_injection_indices_on_utilizations(resource_datetimes, resource_fault_end_datetimes)

    return resource_fault_start_indices, resource_fault_end_indices


def draw_heatmap(x_labels, y_labels, heatmap_data):
    # create a 2D array of data from the list of tuples
    array_data = np.zeros((len(y_labels), len(x_labels)))
    for item in heatmap_data:
        array_data[y_labels[item[1]], x_labels[item[0]]] = item[2]
    # create a heatmap with the data
    fig, ax = plt.subplots(figsize=(6, 4))
    heatmap = ax.pcolor(array_data, cmap='Reds')
    # add a colorbar legend to the heatmap
    plt.colorbar(heatmap)
    # add labels to the axes
    ax.set_xticks(np.arange(0.5, len(x_labels)), list(x_labels.keys()))
    ax.set_yticks(np.arange(0.5, len(y_labels)), list(y_labels.keys()))
    plt.xticks(rotation=90)
    # increase the bottom margin of the plot
    fig.subplots_adjust(bottom=0.2)
    fig.suptitle('Impact on Network Utilization Time Heatmap', fontsize=16, fontweight='bold')
    # display the plot
    plt.show()

def normalized_average(faulties, fault_frees):
    # avg_faulties = utils.get_avg_without_outlier(faulties)
    # avg_fault_frees = utils.get_avg_without_outlier(fault_frees)
    avg_faulties = sum(faulties)/len(faulties)
    avg_fault_frees = sum(fault_frees)/len(fault_frees)

    return avg_faulties-avg_fault_frees/avg_fault_frees

def draw_fault_free_comparisons():
    no_fault_cpu_data = []
    no_fault_memory_data = []
    no_fault_network_data = []
    no_fault_disk_data = []

    apps = ['FPO-SIN', 'FFT', 'SORT', 'DD', 'IPERF', 'IP', 'SA', 'OD-CPU']

    for app in apps:
        print("************ Summary of app: {0},  No-Fault".format(app))
        app_fault_statistics = AppFaultStatistics(app, 'No-Fault')

        no_fault_cpu_data.append((app,
                                  get_avg_without_outlier(app_fault_statistics.get_fault_free_values('CPU', 'USR')),
                                  get_std_without_outlier(app_fault_statistics.get_fault_free_values('CPU', 'USR'))))
        no_fault_memory_data.append((app,
                                  get_avg_without_outlier(app_fault_statistics.get_fault_free_values('MEM', '')),
                                  get_std_without_outlier(app_fault_statistics.get_fault_free_values('MEM', ''))))
        no_fault_network_data.append((app,
                                     get_avg_without_outlier(app_fault_statistics.get_fault_free_values('NET', 'TRA')),
                                     get_std_without_outlier(app_fault_statistics.get_fault_free_values('NET', 'TRA'))))
        no_fault_disk_data.append((app,
                                     get_avg_without_outlier(app_fault_statistics.get_fault_free_values('DISK', '')),
                                     get_std_without_outlier(app_fault_statistics.get_fault_free_values('DISK', ''))))
    # extract the labels, values, and errors into separate lists
    labels = [x[0] for x in no_fault_cpu_data]
    cpu_values = [x[1] for x in no_fault_cpu_data]
    cpu_errors = [x[2] for x in no_fault_cpu_data]
    memory_values = [x[1] for x in no_fault_memory_data]
    memory_errors = [x[2] for x in no_fault_memory_data]
    network_values = [x[1] for x in no_fault_network_data]
    network_errors = [x[2] for x in no_fault_network_data]
    disk_values = [x[1] for x in no_fault_disk_data]
    disk_errors = [x[2] for x in no_fault_disk_data]

    # create a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(8, 8))

    # plot the data in each subplot
    axs[0, 0].bar(labels, cpu_values, yerr=cpu_errors, capsize=4)
    axs[0, 0].set_title('CPU Utilization', fontweight='bold')
    axs[0, 0].set_ylabel('CPU USR Utilization (%)', fontweight='bold')
    axs[0, 0].grid(which="major")
    axs[0, 1].bar(labels, memory_values, yerr=memory_errors, capsize=4)
    axs[0, 1].set_title('Memory Utilization', fontweight='bold')
    axs[0, 1].set_ylabel('Memory Utilization (%)', fontweight='bold')
    axs[0, 1].grid(which="major")
    axs[1, 0].bar(labels, network_values, yerr=network_errors, capsize=4)
    axs[1, 0].set_title('Network Utilization', fontweight='bold')
    axs[1, 0].set_ylabel('Network Receiving Packets Rate (kB/s)', fontweight='bold')
    axs[1, 0].grid(which="major")
    axs[1, 1].bar(labels, disk_values, yerr=disk_errors, capsize=4)
    axs[1, 1].set_title('Disk Utilization', fontweight='bold')
    axs[1, 1].set_ylabel('Disk utilization (%)', fontweight='bold')
    axs[1, 1].grid(which="major")

    # adjust spacing between subplots
    fig.tight_layout()
    plt.show()



if __name__ == '__main__':
    x_labels = {'FPO-SIN-CPU%USR': 0, 'FPO-SIN-CPU%SYS': 1, 'FFT-CPU%USR': 2, 'FFT-CPU%SYS': 3,
                'SORT-CPU%USR': 4, 'SORT-CPU%SYS': 5, 'DD-CPU%USR': 6, 'DD-CPU%SYS': 7,
                'IPERF-CPU%USR': 8, 'IPERF-CPU%SYS': 9, 'IP-CPU%USR': 10, 'IP-CPU%SYS': 11, 'SA-CPU%USR': 12,
                'SA-CPU%SYS': 13, 'OD-CPU-CPU%USR': 14, 'OD-CPU-CPU%SYS': 15,
                'FPO-SIN-MEM': 16, 'FFT-MEM': 17, 'SORT-MEM': 18, 'DD-MEM': 19, 'IPERF-MEM': 20,
                'IP-MEM': 21, 'SA-MEM': 22, 'OD-CPU-MEM': 23,
                'FPO-SIN-DISK': 24, 'FFT-DISK': 25, 'SORT-DISK': 26, 'DD-DISK': 27, 'IPERF-DISK': 28,
                'IP-DISK': 29, 'SA-DISK': 30, 'OD-CPU-DISK': 31}\
        # ,
        #         'FPO-SIN-NET-REC': 20, 'FFT-NET-REC': 21, 'SORT-NET-REC': 22, 'DD-NET-REC': 23, 'IPERF-NET-REC': 24,
        #         'FPO-SIN-NET-TRA': 25, 'FFT-NET-TRA': 26, 'SORT-NET-TRA': 27, 'DD-NET-TRA': 28, 'IPERF-NET-TRA': 29
        #         }

    x_network_labels = {'FPO-SIN-NET-REC': 0, 'FFT-NET-REC': 1, 'SORT-NET-REC': 2, 'DD-NET-REC': 3, 'IPERF-NET-REC': 4,
                        'IP-NET-REC': 5, 'SA-NET-REC': 6, 'OD-CPU-NET-REC': 7,
                'FPO-SIN-NET-TRA': 8, 'FFT-NET-TRA': 9, 'SORT-NET-TRA': 10, 'DD-NET-TRA': 11, 'IPERF-NET-TRA': 12,
                        'IP-NET-TRA': 13, 'SA-NET-TRA': 14, 'OD-CPU-NET-TRA': 15}

    x_latencies_labels = {'FPO-SIN-LATENCY': 0, 'FFT-LATENCY': 1, 'SORT-LATENCY': 2, 'DD-LATENCY': 3, 'IPERF-LATENCY': 4,
                          'IP-LATENCY': 5, 'SA-LATENCY': 6, 'OD-CPU-LATENCY': 7}

    y_labels = {'No-Fault': 0, 'CPU-20': 1, 'CPU-80': 2, 'MEM-20%': 3, 'MEM-80%': 4, 'IO-100': 5,
                'PF-0': 6, 'CCHE-0': 7, 'CTXS-10000': 8}

    y_diff_labels = {'CPU-20': 0, 'CPU-80': 1, 'MEM-20%': 2, 'MEM-80%': 3, 'IO-100': 4,
                'PF-0': 5, 'CCHE-0': 6, 'CTXS-10000': 7}

    jitter_heatmap_data = []
    diffs_heatmap_data = []
    network_diffs_heatmapt_date = []
    network_jitter_heatmap_date = []

    latency_jitter_data = []
    latency_diffs_data = []

    latency_data = []


    app_fault_statistics = AppFaultStatistics('IPERF', 'CPU-20')
    app_fault_statistics.plot_resource_with_residual('CPU', 'SYS', show_injection_times=True)

    # draw_fault_free_comparisons()

    apps = []
    faults = []

    # apps = ['FPO-SIN']
    # faults = ['CPU-20']
    # apps = ['IP', 'SA', 'OD-CPU']
    # apps = ['FPO-SIN', 'FFT', 'SORT', 'DD', 'IPERF', 'IP', 'SA', 'OD-CPU']
    # faults = [ 'CPU-80', 'MEM-20%', 'MEM-80%', 'IO-100', 'PF-0', 'CCHE-0', 'CTXS-10000']

    for app in apps:
        no_fault_written = False
        for fault in faults:
            print("************ Summary of app: {0}, fault: {1}".format(app, fault))
            app_fault_statistics = AppFaultStatistics(app, fault)

            diffs_heatmap_data.append([(app + '-CPU%SYS'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('CPU', 'SYS'),
                app_fault_statistics.get_fault_free_values('CPU', 'SYS'))])
            diffs_heatmap_data.append([(app + '-CPU%USR'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('CPU', 'USR'),
                app_fault_statistics.get_fault_free_values('CPU', 'USR'))])
            diffs_heatmap_data.append([(app + '-MEM'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('MEM', ''),
                app_fault_statistics.get_fault_free_values('MEM', ''))])
            diffs_heatmap_data.append([(app + '-DISK'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('DISK', ''),
                app_fault_statistics.get_fault_free_values('DISK', ''))])
            network_diffs_heatmapt_date.append([(app + '-NET-REC'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('NET', 'REC'),
                app_fault_statistics.get_fault_free_values('NET', 'REC'))])
            network_diffs_heatmapt_date.append([(app + '-NET-TRA'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('NET', 'TRA'),
                app_fault_statistics.get_fault_free_values('NET', 'TRA'))])

            latency_diffs_data.append([(app + '-LATENCY'), fault, normalized_average(
                app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME'),
                app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME'))])

            jitter_heatmap_data.append([(app + '-CPU%SYS'), fault, jitter(app_fault_statistics.get_faulty_values('CPU', 'SYS'))])
            jitter_heatmap_data.append([(app + '-CPU%USR'), fault, jitter(app_fault_statistics.get_faulty_values('CPU', 'USR'))])
            jitter_heatmap_data.append([(app + '-MEM'), fault, jitter(app_fault_statistics.get_faulty_values('MEM',''))])
            jitter_heatmap_data.append([(app + '-DISK'), fault, jitter(app_fault_statistics.get_faulty_values('DISK', ''))])
            network_jitter_heatmap_date.append([(app + '-NET-REC'), fault, jitter(app_fault_statistics.get_faulty_values('NET', 'REC'))])
            network_jitter_heatmap_date.append([(app + '-NET-TRA'), fault, jitter(app_fault_statistics.get_faulty_values('NET', 'TRA'))])
            latency_jitter_data.append([(app + '-LATENCY'), fault, jitter(app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME'))])
            # jitter_heatmap_data.append([(app + '-NET-UTIL'), fault, jitter(app_fault_statistics.get_faulty_values('NET', 'UTIL'))])
            # jitter_heatmap_data.append([(app + '-CPU%SYS'), 'No-Fault',
            #                             app_fault_statistics.jitter_faulty_fault_free('CPU', 'SYS', is_faulty=True)])
            # jitter_heatmap_data.append([(app + '-CPU%USR'), 'No-Fault',
            #                             app_fault_statistics.jitter_faulty_fault_free('CPU', 'USR', is_faulty=True)])
            # jitter_heatmap_data.append(
            #     [(app + '-MEM'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('MEM', '', is_faulty=True)])
            # jitter_heatmap_data.append([(app + '-DISK'), 'No-Fault',
            #                             app_fault_statistics.jitter_faulty_fault_free('DISK', '', is_faulty=True)])
            # network_jitter_heatmap_date.append([(app + '-NET-REC'), 'No-Fault',
            #                                     app_fault_statistics.jitter_faulty_fault_free('NET', 'REC',
            #                                                                                   is_faulty=True)])
            # network_jitter_heatmap_date.append([(app + '-NET-TRA'), 'No-Fault',
            #                                     app_fault_statistics.jitter_faulty_fault_free('NET', 'TRA',
            #                                                                                   is_faulty=True)])

            latency_data.append(((app + '-' + fault),
                                 utils.get_avg_without_outlier(app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME')),
                                 utils.get_std_without_outlier(app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME'))))

            if not no_fault_written:
                # jitter_heatmap_data.append([(app + '-CPU%SYS'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('CPU', 'SYS', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-CPU%USR'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('CPU', 'USR', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-MEM'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('MEM', '', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-DISK'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('DISK', '', is_faulty=False)])
                # network_jitter_heatmap_date.append([(app + '-NET-REC'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('NET', 'REC', is_faulty=False)])
                # network_jitter_heatmap_date.append([(app + '-NET-TRA'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('NET', 'TRA', is_faulty=False)])

                jitter_heatmap_data.append([(app + '-CPU%SYS'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('CPU', 'SYS'))])
                jitter_heatmap_data.append([(app + '-CPU%USR'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('CPU', 'USR'))])
                jitter_heatmap_data.append([(app + '-MEM'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('MEM', ''))])
                jitter_heatmap_data.append([(app + '-DISK'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('DISK', ''))])
                network_jitter_heatmap_date.append([(app + '-NET-REC'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'REC'))])
                network_jitter_heatmap_date.append([(app + '-NET-TRA'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'TRA'))])
                latency_jitter_data.append([(app + '-LATENCY'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME'))])


                # jitter_heatmap_data.append([(app + '-NET-UTIL'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'UTIL'))])
                latency_data.append(((app + '-No-Fault'),
                                     utils.get_avg_without_outlier(app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME')),
                                     utils.get_std_without_outlier(app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME'))))
                no_fault_written = True


    draw_heatmap(x_labels, y_labels, jitter_heatmap_data)
    # draw_heatmap(x_labels, y_diff_labels, diffs_heatmap_data)
    # draw_heatmap(x_network_labels, y_diff_labels, network_diffs_heatmapt_date)
    # draw_heatmap(x_network_labels, y_labels, network_jitter_heatmap_date)
    # draw_heatmap(x_latencies_labels, y_labels, latency_jitter_data)
    # draw_heatmap(x_latencies_labels, y_labels, latency_diffs_data)

#############################################
    # extract the labels, values, and errors into separate lists
    # labels = [x[0] for x in latency_data]
    # values = [x[1] for x in latency_data]
    # errors = [x[2] for x in latency_data]
    #
    # # create a bar chart of the values with labels on the x-axis and error bars
    # plt.bar(labels, values, yerr=errors, capsize=4)
    #
    # # add labels to the axes
    # plt.xlabel('Application-Fault')
    # plt.ylabel('Computation Time (ms)')
    # plt.xticks(rotation=90)
    # plt.subplots_adjust(bottom=0.2)
    # plt.suptitle('Impact on Latency Computation Time', fontsize=16, fontweight='bold')
    #
    # # fig.subplots_adjust(bottom=0.2)
    #
    # # display the plot
    # plt.show()

    # plot_single_resource(app, fault, compute_times, fault_start_indices, fault_end_indices, show_injection_times=True)





