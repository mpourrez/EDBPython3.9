import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import math
import csv
from .. import configs

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
        self.experiment_duration = configs.EXPERIMENT_DURATION
        self.read_all_saved_statistics()

    def get_base_date(self):
        if self.app == 'FFT' or self.app == 'FPO-SIN' or self.app == 'FPO-SQRT' or self.app == 'SORT':
            if self.fault != 'No-Fault':
                return '2023-05-23 '

        if self.app == 'DD' and (self.fault == 'CPU-20' or self.fault == 'CPU-60' or
                                 self.fault == 'CPU-90' or self.fault == 'MEM-20%'):
            return '2023-05-23 '
        return '2023-05-24 '


    def read_all_saved_statistics(self):
        self.get_fault_injection_times()
        if len(self.fault_start_times) == 0:
            self.experiment_duration = configs.NUMBER_OF_FAULT_FREE_ROUNDS * configs.FAULT_FREE_DURATIONS
        self.get_cpu_utilization()
        self.get_cpu_temperatures()
        self.get_latencies()
        self.get_iostat()
        self.get_network_statistics()
        self.get_memory_utilization()

    def get_resource_datetimes(self, resource):
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
        if resource == 'CPU' and rtype == 'SYS':
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
        elif resource == 'LATENCY' and rtype == 'COM-TIME':
            values = self.compute_times
        elif resource == 'LATENCY' and rtype == 'TRA-TIME':
            values = self.transmission_times
        else:
            values = self.cpu_temperatures
        return values

    def get_resource_metric(self, resource, rtype):
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
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetime,
                                                                                 self.fault_start_times)
        _, resource_faulty_values = get_fault_free_faulty_values(resource_values, fault_start_indices,
                                                                 fault_end_indices)
        return resource_faulty_values

    def get_fault_free_values(self, resource, rtype):
        resource_datetime = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetime,
                                                                                 self.fault_start_times)
        resource_fault_free_values, _ = get_fault_free_faulty_values(resource_values, fault_start_indices,
                                                                     fault_end_indices)
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
        date = self.get_base_date()
        cpu_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-CPU.txt',
                             delimiter='\s+', skiprows=2)
        cpu_times = cpu_df.iloc[:, 0]
        self.cpu_datetimes = []
        for t in cpu_times:
            if 'Average' not in t:
                cpu_datetime = datetime.datetime.strptime(date + t + ' PM', '%Y-%m-%d %I:%M:%S %p')
                self.cpu_datetimes.append(cpu_datetime)
        self.cpu_datetimes = self.cpu_datetimes[:self.experiment_duration + 1]
        self.user_cpu_utilization = cpu_df['%usr'][:self.experiment_duration + 1]
        self.sys_cpu_utilization = cpu_df['%sys'][:self.experiment_duration + 1]
        self.total_cpu_utilization = 100 - cpu_df['%idle'][:self.experiment_duration + 1]

    #############################################
    #########     CPU Temperatures    ###########
    #############################################
    def get_cpu_temperatures(self):
        cpu_temp_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-TEMP.txt',
                                  delimiter=',')
        cpu_temp_times = cpu_temp_df['Timestamp_ms']
        self.cpu_temp_datetimes = []

        first_date = self.cpu_datetimes[0]
        first_index = 0
        last_date = self.cpu_datetimes[len(self.cpu_datetimes) - 1]
        last_index = 0
        for t in cpu_temp_times:
            cpu_temp_datetime = get_datetime_from_timestamp(self.app, self.fault, t)
            cpu_temp_datetime = cpu_temp_datetime.replace(microsecond=0)
            if cpu_temp_datetime < first_date:
                first_index += 1
                continue
            if cpu_temp_datetime > last_date:
                break
            self.cpu_temp_datetimes.append(cpu_temp_datetime)
            last_index += 1
        self.cpu_temperatures = cpu_temp_df['CPU_Temp'][first_index:last_index + 1]

    #############################################
    #########     Latencies    ##################
    #############################################
    def get_latencies(self):
        latencies_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-Latency.csv',
                                   delimiter=',')
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
        date = '2023-05-24 '
        io_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-IO.txt', delimiter='\s+',
                            skiprows=3)
        self.io_datetimes = []
        self.disk_utilization = []  # %util
        writes_ps = []  # w/s
        write_kilobytes = []  # wkB/s
        write_wait_times = []  # w_await
        first = True
        first_date = self.cpu_datetimes[0]
        last_date = self.cpu_datetimes[len(self.cpu_datetimes) - 1]
        for i in range(len(io_df)):
            if '/2023' in io_df.iloc[:, 0][i]:
                io_time = io_df.iloc[:, 1][i]
                io_datetime = datetime.datetime.strptime(date + io_time + ' PM', '%Y-%m-%d %I:%M:%S %p')
                io_datetime = io_datetime.replace(microsecond=0)
                if io_datetime < first_date:
                    continue
                if io_datetime > last_date:
                    break
                if first:
                    first_missing_date = io_datetime.replace(second=(io_datetime.second - 1))
                    if first_missing_date < first_date:
                        continue
                    self.io_datetimes.append(first_missing_date)
                    first = False
                self.io_datetimes.append(io_datetime)
            elif io_df.iloc[:, 0][i] == 'mmcblk0':
                self.disk_utilization.append(float(io_df.iloc[:, 22][i]))

    #############################################
    #########     NEtwork Utilizations    #######
    #############################################
    def get_network_statistics(self):
        date = self.get_base_date()

        net_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-NET.txt',
                             delimiter='\s+',
                             skiprows=2)
        self.net_datetimes = []
        self.net_utilizations = []  # %ifutil
        self.net_receive_rates = []  # rxkB/s The number of kilobytes received per second.
        self.net_transmit_rates = []  # txkB/s: The number of kilobytes transmitted per second

        last_date = self.cpu_datetimes[len(self.cpu_datetimes) - 1]
        for i in range(len(net_df)):
            if net_df.iloc[:, 2][i] == 'wlan0':
                net_time = net_df.iloc[:, 0][i]
                net_datetime = datetime.datetime.strptime(date + net_time + ' PM', '%Y-%m-%d %I:%M:%S %p')
                if net_datetime > last_date:
                    break
                self.net_datetimes.append(net_datetime)

                self.net_utilizations.append(float(net_df.iloc[:, 10][i]))
                self.net_receive_rates.append(float(net_df.iloc[:, 5][i]))
                self.net_transmit_rates.append(float(net_df.iloc[:, 6][i]))

        # if self.app=='IPERF':
        #     index_of_zero = 0
        #     for i, val in enumerate(self.net_receive_rates[1:], start=1):
        #         if all(x == 0.0 for x in self.net_receive_rates[i:]):
        #             index_of_zero = i
        #             break
        #     # index_of_zero = net_float_receive_rates.index(19291.64)
        #     print(index_of_zero)
        #     self.net_utilizations = self.net_utilizations[:index_of_zero]
        #     self.net_receive_rates = self.net_receive_rates[:index_of_zero]
        #     self.net_transmit_rates = self.net_transmit_rates[:index_of_zero]
        #     self.net_datetimes = self.net_datetimes[:index_of_zero]

    #############################################
    #########     Memory Utilizations    ########
    #############################################
    def get_memory_utilization(self):
        date = self.get_base_date()
        mem_df = pd.read_csv('results_over_time/raspberrypi/' + self.app + '-' + self.fault + '-MEM.txt',
                             delimiter='\s+', skiprows=2)
        mem_times = mem_df.iloc[:, 0]
        self.mem_datetimes = []
        for t in mem_times:
            if 'Average' not in t:
                mem_datetime = datetime.datetime.strptime(date + t + ' PM', '%Y-%m-%d %I:%M:%S %p')
                self.mem_datetimes.append(mem_datetime)

        self.mem_utilization = mem_df['%memused'][:self.experiment_duration + 1]
        self.mem_datetimes = self.mem_datetimes[:self.experiment_duration + 1]

    ######################################################################################################################
    #################################     END: Reading Files      ########################################################
    ######################################################################################################################

    def plot_resource(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes,
                                                                                 self.fault_start_times)
        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label='memused')
        if show_injection_times:
            for start in fault_start_indices:
                axs.axvline(x=resource_datetimes[start], color='r')
            for end in fault_end_indices:
                axs.axvline(x=resource_datetimes[end], color='b')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource + '-' + rtype + ' (' + resource_metric + ')', fontsize=16, fontweight='bold')
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource + '-' + rtype + ' Utilization Plot for App: ' + self.app + ' - Fault: ' + self.fault,
                     fontsize=16, fontweight='bold')
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

        average_fault_free_jitter = sum(fault_free_jitters) / len(fault_free_jitters)
        average_faulty_jitter = sum(faulty_jitters) / len(faulty_jitters)

        if is_faulty:
            print("faulty avg: {0}".format(average_faulty_jitter))
            return average_faulty_jitter
        print("fault free avg: {0}".format(average_fault_free_jitter))
        return average_fault_free_jitter

    def plot_resource(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes,
                                                                                 self.fault_start_times)
        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label='memused')
        if show_injection_times:
            for start in fault_start_indices:
                axs.axvline(x=resource_datetimes[start], color='r')
            for end in fault_end_indices:
                axs.axvline(x=resource_datetimes[end], color='b')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource + '-' + rtype + ' (' + resource_metric + ')', fontsize=16, fontweight='bold')
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource + '-' + rtype + ' Utilization Plot for App: ' + self.app + ' - Fault: ' + self.fault,
                     fontsize=16, fontweight='bold')
        plt.show()

    def plot_resource_with_residual(self, resource, rtype, show_injection_times):
        resource_datetimes = self.get_resource_datetimes(resource)
        resource_values = self.get_resource_values(resource, rtype)
        resource_metric = self.get_resource_metric(resource, rtype)
        fault_start_indices, fault_end_indices = extract_fault_start_end_indices(resource_datetimes,
                                                                                 self.fault_start_times)
        print(self.fault_start_times)
        print(resource_datetimes)

        fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))
        axs.plot(resource_datetimes, resource_values, label=resource + '-' + rtype)

        residual_means = []
        residual_jitters = []
        residual_dates = []
        if show_injection_times:
            start_ind = 0
            for fault_start, fault_end in zip(fault_start_indices, fault_end_indices):
                axs.axvline(x=resource_datetimes[fault_start], color='r')
                axs.axvline(x=resource_datetimes[fault_end], color='b')

                fault_free_middle_date = resource_datetimes[start_ind] + (
                            resource_datetimes[fault_start] - resource_datetimes[start_ind]) / 2
                faulty_middle_date = resource_datetimes[fault_start] + (
                            resource_datetimes[fault_end] - resource_datetimes[fault_start]) / 2
                fault_free_values = resource_values[start_ind:fault_start]
                faulty_values = resource_values[fault_start:fault_end]

                residual_dates.append(fault_free_middle_date)
                residual_dates.append(faulty_middle_date)
                residual_means.append(sum(fault_free_values) / len(fault_free_values))
                residual_means.append(sum(faulty_values) / len(faulty_values))
                residual_jitters.append(jitter(fault_free_values))
                residual_jitters.append(jitter(faulty_values))
                start_ind = fault_end + 1

            extra_end = 85
            if resource == 'NET':
                extra_end = 1

            fault_free_middle_date = resource_datetimes[len(resource_datetimes) - extra_end] + (
                    resource_datetimes[len(resource_datetimes) - extra_end] - resource_datetimes[start_ind]) / 2
            fault_free_values = resource_values[start_ind:len(resource_datetimes) - extra_end]
            residual_dates.append(fault_free_middle_date)
            residual_means.append(sum(fault_free_values) / len(fault_free_values))
            residual_jitters.append(jitter(fault_free_values))

        axs.plot(residual_dates, residual_means, label='residual-mean')
        axs.plot(residual_dates, residual_jitters, label='residual-jitter')
        axs.set_xlabel('Time', fontsize=16, fontweight='bold')
        axs.set_ylabel(resource + '-' + rtype + ' (' + resource_metric + ')', fontsize=16, fontweight='bold')
        # axs.legends()
        # axs.set_xlim(right=230)
        # axs.set_xlim(left=-10)
        axs.grid(which="major")
        fig.suptitle(resource + '-' + rtype + ' Utilization Plot for App: ' + self.app + ' - Fault: ' + self.fault,
                     fontsize=16, fontweight='bold')
        plt.show()

    def get_resource_summary_matrix(self):
        summary_matrix = {}

        for (cpu_date, cpu_user, cpu_sys, cpu_total) in \
                zip(self.cpu_datetimes, self.user_cpu_utilization, self.sys_cpu_utilization,
                    self.total_cpu_utilization):
            result_summary = ResultSummary(cpu_user, cpu_sys, cpu_total, 'No-Fault')
            summary_matrix[cpu_date] = result_summary

        for (cpu_temp_date, cpu_temp) in zip(self.cpu_temp_datetimes, self.cpu_temperatures):
            if cpu_temp_date in summary_matrix.keys():
                summary_matrix[cpu_temp_date].cpu_temp = cpu_temp

        for (mem_date, mem) in zip(self.mem_datetimes, self.mem_utilization):
            if mem_date in summary_matrix.keys():
                summary_matrix[mem_date].mem = mem

        for (disk_date, disk) in zip(self.io_datetimes, self.disk_utilization):
            if disk_date in summary_matrix.keys():
                summary_matrix[disk_date].disk = disk

        for (net_date, net_rec, net_tra) in zip(self.net_datetimes, self.net_receive_rates, self.net_transmit_rates):
            if net_date in summary_matrix.keys():
                summary_matrix[net_date].net_rec = net_rec
                summary_matrix[net_date].net_tra = net_tra

        for (response_datetime, compute_time, transmit_time) in \
                zip(self.response_datetimes, self.compute_times, self.transmission_times):
            if response_datetime.replace(microsecond=0) in summary_matrix.keys():
                summary_matrix[response_datetime.replace(microsecond=0)].com_t = compute_time
                summary_matrix[response_datetime.replace(microsecond=0)].tra_t = transmit_time

        # Update fault labels according to injection times
        fault_end_datetimes = [dt + datetime.timedelta(seconds=configs.FAULT_INJECTION_DURATION) for dt in self.fault_start_times]
        for (start_injection, end_injection) in zip(self.fault_start_times, fault_end_datetimes):
            # print('{0} - {1}'.format(start_injection, end_injection))
            for key in summary_matrix.keys():
                # print(key)
                if start_injection <= key <= end_injection:
                    summary_matrix[key].label = self.fault
            # print('-------------------------------')


        return summary_matrix

        # for key in summary_matrix.keys():
        #     print('{0} -----  {1}'.format(key, summary_matrix[key]))


class ResultSummary:
    def __init__(self, cpu_user, cpu_sys, cpu_tot, label):
        super().__init__()
        self.cpu_user = cpu_user
        self.cpu_sys = cpu_sys
        self.cpu_tot = cpu_tot
        self.cpu_temp = '-----'
        self.mem = None
        self.disk = None
        self.net_rec = None
        self.net_tra = None
        self.com_t = '-----'
        self.tra_t = '-----'
        self.label = label

    def __str__(self):
        if self.cpu_temp == '-----':
            return 'cpu_usr: {0:.2f} - cpu_sys: {1:.2f} - cpu_tot: {2:.2f} - cpu_temp:{3} - mem: {4:.2f} - ' \
                   'disk: {5:.2f} - net_rec: {6:.2f} - net_tra: {7:.2f} - compute_time: {8}, ' \
                   'transmit_time:{9} - label: {10}'.format(
                self.cpu_user, self.cpu_sys, self.cpu_tot, self.cpu_temp, self.mem, self.disk, self.net_rec,
                self.net_tra, self.com_t, self.tra_t, self.label)

        return 'cpu_usr: {0:.2f} - cpu_sys: {1:.2f} - cpu_tot: {2:.2f} - cpu_temp:{3:.2f} - mem: {4:.2f} - ' \
               'disk: {5:.2f} - net_rec: {6:.2f} - net_tra: {7:.2f} - compute_time: {8}, ' \
                   'transmit_time:{9} - label: {10}'.format(
                self.cpu_user, self.cpu_sys, self.cpu_tot, self.cpu_temp, self.mem, self.disk, self.net_rec,
                self.net_tra, self.com_t, self.tra_t, self.label)


class AppStatistics:
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.combine_statistics()

    def combine_statistics(self):
        with open('results_over_time/raspberrypi/summary-'+self.app+'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            headers = ['Time', 'CPU_USER', 'CPU_SYS', 'CPU_TOT', 'CPU_TEMP', 'MEM', 'DISK', 'NET_REC', 'NET_TRA',
                       'COM_T', 'TRA_T', 'Label']
            writer.writerow(headers)

            # Write No Fault Results
            app_no_fault_statistics = AppFaultStatistics(self.app, 'No-Fault')
            summary_matrix = app_no_fault_statistics.get_resource_summary_matrix()
            for key in summary_matrix.keys():
                value = summary_matrix[key]
                row = [key, value.cpu_user, value.cpu_sys,  ("%.2f" % value.cpu_tot)]
                rest_row = [value.mem, value.disk, value.net_rec, value.net_tra, value.com_t, value.tra_t, value.label]
                if value.cpu_temp!='-----':
                    row.append("%.2f" % value.cpu_temp)
                else:
                    row.append('-')
                row.extend(rest_row)
                writer.writerow(row)

            # Write Faulty Results
            for fault in configs.FAULTS:
                for fault_config in fault.fault_config:
                    print('{0}-{1}'.format(fault.abbreviation, fault_config))
                    app_fault_statistics = AppFaultStatistics(self.app, '{0}-{1}'.format(fault.abbreviation,
                                                                                         fault_config))
                    summary_matrix = app_fault_statistics.get_resource_summary_matrix()
                    for key in summary_matrix.keys():
                        value = summary_matrix[key]
                        row = [key, value.cpu_user, value.cpu_sys, ("%.2f" % value.cpu_tot)]
                        rest_row = [value.mem, value.disk, value.net_rec, value.net_tra, value.com_t, value.tra_t,
                                    value.label]
                        if value.cpu_temp != '-----':
                            row.append("%.2f" % value.cpu_temp)
                        else:
                            row.append('-')
                        row.extend(rest_row)
                        writer.writerow(row)



def extract_fault_start_end_indices(resource_datetimes, fault_start_times):
    resource_fault_start_indices = find_fault_injection_indices_on_utilizations(resource_datetimes, fault_start_times)
    resource_fault_end_datetimes = [dt + datetime.timedelta(seconds=30) for dt in fault_start_times]
    resource_fault_end_indices = find_fault_injection_indices_on_utilizations(resource_datetimes,
                                                                              resource_fault_end_datetimes)

    return resource_fault_start_indices, resource_fault_end_indices

def find_fault_injection_indices_on_utilizations(utilization_times, fault_injection_times):
    index = 0
    fault_index = 0

    fault_injection_indices = []
    while index < len(utilization_times):
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
        if index >= len(fault_start_indices) or i < fault_start_indices[index] and i < fault_end_indices[index]:
            fault_free_values.append(values[i])
        elif i >= fault_start_indices[index] and i >= fault_end_indices[index] and index < len(fault_start_indices):
            index += 1
            faulty_values.append(values[i])
        else:
            faulty_values.append(values[i])
    return fault_free_values, faulty_values

def get_datetime_from_timestamp(app, fault, timestamp):
    fault_start_time = datetime.datetime.fromtimestamp(timestamp / 1000)

def jitter(values):
    n = len(values)
    if n <= 1:
        return 0.0
    mean = sum(values) / float(n)
    variance = sum((x - mean) ** 2 for x in values) / float(n - 1)
    return math.sqrt(variance)