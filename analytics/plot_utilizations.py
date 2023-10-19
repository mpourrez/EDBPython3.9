import matplotlib.pyplot as plt
import numpy as np
import utils
from app_statistics import *


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



def normalized_average(faulties, fault_frees):
    # avg_faulties = utils.get_avg_without_outlier(faulties)
    # avg_fault_frees = utils.get_avg_without_outlier(fault_frees)
    avg_faulties = sum(faulties) / len(faulties)
    avg_fault_frees = sum(fault_frees) / len(fault_frees)

    return avg_faulties - avg_fault_frees / avg_fault_frees


def draw_fault_free_comparisons():
    no_fault_cpu_data = []
    no_fault_memory_data = []
    no_fault_network_data = []
    no_fault_disk_data = []

    apps = ['AE']  # , 'FPO-SIN', 'FPO-SQRT', 'SORT', 'DD', 'IPERF',
    # 'IP', 'SA', 'IC-A-CPU', 'IC-S-CPU', 'OD-CPU', 'PS', 'AE', 'OT-CPU']
    # ['FPO-SIN', 'FFT', 'SORT', 'DD', 'IPERF', 'IP', 'SA', 'OD-CPU']

    for app in apps:
        print("************ Summary of app: {0},  No-Fault".format(app))
        app_fault_statistics = AppFaultStatistics(app, 'No-Fault')

    #     no_fault_cpu_data.append((app,
    #                               get_avg_without_outlier(app_fault_statistics.get_fault_free_values('CPU', 'USR')),
    #                               get_std_without_outlier(app_fault_statistics.get_fault_free_values('CPU', 'USR'))))
    #     no_fault_memory_data.append((app,
    #                               get_avg_without_outlier(app_fault_statistics.get_fault_free_values('MEM', '')),
    #                               get_std_without_outlier(app_fault_statistics.get_fault_free_values('MEM', ''))))
    #     no_fault_network_data.append((app,
    #                                  get_avg_without_outlier(app_fault_statistics.get_fault_free_values('NET', 'TRA')),
    #                                  get_std_without_outlier(app_fault_statistics.get_fault_free_values('NET', 'TRA'))))
    #     no_fault_disk_data.append((app,
    #                                  get_avg_without_outlier(app_fault_statistics.get_fault_free_values('DISK', '')),
    #                                  get_std_without_outlier(app_fault_statistics.get_fault_free_values('DISK', ''))))
    # # extract the labels, values, and errors into separate lists
    # labels = [x[0] for x in no_fault_cpu_data]
    # cpu_values = [x[1] for x in no_fault_cpu_data]
    # cpu_errors = [x[2] for x in no_fault_cpu_data]
    # memory_values = [x[1] for x in no_fault_memory_data]
    # memory_errors = [x[2] for x in no_fault_memory_data]
    # network_values = [x[1] for x in no_fault_network_data]
    # network_errors = [x[2] for x in no_fault_network_data]
    # disk_values = [x[1] for x in no_fault_disk_data]
    # disk_errors = [x[2] for x in no_fault_disk_data]
    #
    # # create a 2x2 grid of subplots
    # fig, axs = plt.subplots(2, 2, figsize=(8, 8))
    #
    # # plot the data in each subplot
    # axs[0, 0].bar(labels, cpu_values, yerr=cpu_errors, capsize=4)
    # axs[0, 0].set_title('CPU Utilization', fontweight='bold')
    # axs[0, 0].set_ylabel('CPU USR Utilization (%)', fontweight='bold')
    # axs[0, 0].grid(which="major")
    # axs[0, 1].bar(labels, memory_values, yerr=memory_errors, capsize=4)
    # axs[0, 1].set_title('Memory Utilization', fontweight='bold')
    # axs[0, 1].set_ylabel('Memory Utilization (%)', fontweight='bold')
    # axs[0, 1].grid(which="major")
    # axs[1, 0].bar(labels, network_values, yerr=network_errors, capsize=4)
    # axs[1, 0].set_title('Network Utilization', fontweight='bold')
    # axs[1, 0].set_ylabel('Network Receiving Packets Rate (kB/s)', fontweight='bold')
    # axs[1, 0].grid(which="major")
    # axs[1, 1].bar(labels, disk_values, yerr=disk_errors, capsize=4)
    # axs[1, 1].set_title('Disk Utilization', fontweight='bold')
    # axs[1, 1].set_ylabel('Disk utilization (%)', fontweight='bold')
    # axs[1, 1].grid(which="major")
    #
    # # adjust spacing between subplots
    # fig.tight_layout()
    # plt.show()


def draw_heatmaps():
    x_labels = {'FPO-SIN-CPU%USR': 0, 'FPO-SIN-CPU%SYS': 1, 'FFT-CPU%USR': 2, 'FFT-CPU%SYS': 3,
                'SORT-CPU%USR': 4, 'SORT-CPU%SYS': 5, 'DD-CPU%USR': 6, 'DD-CPU%SYS': 7,
                'IPERF-CPU%USR': 8, 'IPERF-CPU%SYS': 9, 'IP-CPU%USR': 10, 'IP-CPU%SYS': 11, 'SA-CPU%USR': 12,
                'SA-CPU%SYS': 13, 'OD-CPU-CPU%USR': 14, 'OD-CPU-CPU%SYS': 15,
                'FPO-SIN-MEM': 16, 'FFT-MEM': 17, 'SORT-MEM': 18, 'DD-MEM': 19, 'IPERF-MEM': 20,
                'IP-MEM': 21, 'SA-MEM': 22, 'OD-CPU-MEM': 23,
                'FPO-SIN-DISK': 24, 'FFT-DISK': 25, 'SORT-DISK': 26, 'DD-DISK': 27, 'IPERF-DISK': 28,
                'IP-DISK': 29, 'SA-DISK': 30, 'OD-CPU-DISK': 31} \
        # ,
    #         'FPO-SIN-NET-REC': 20, 'FFT-NET-REC': 21, 'SORT-NET-REC': 22, 'DD-NET-REC': 23, 'IPERF-NET-REC': 24,
    #         'FPO-SIN-NET-TRA': 25, 'FFT-NET-TRA': 26, 'SORT-NET-TRA': 27, 'DD-NET-TRA': 28, 'IPERF-NET-TRA': 29
    #         }

    x_network_labels = {'FPO-SIN-NET-REC': 0, 'FFT-NET-REC': 1, 'SORT-NET-REC': 2, 'DD-NET-REC': 3, 'IPERF-NET-REC': 4,
                        'IP-NET-REC': 5, 'SA-NET-REC': 6, 'OD-CPU-NET-REC': 7,
                        'FPO-SIN-NET-TRA': 8, 'FFT-NET-TRA': 9, 'SORT-NET-TRA': 10, 'DD-NET-TRA': 11,
                        'IPERF-NET-TRA': 12,
                        'IP-NET-TRA': 13, 'SA-NET-TRA': 14, 'OD-CPU-NET-TRA': 15}

    x_latencies_labels = {'FPO-SIN-LATENCY': 0, 'FFT-LATENCY': 1, 'SORT-LATENCY': 2, 'DD-LATENCY': 3,
                          'IPERF-LATENCY': 4,
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

            jitter_heatmap_data.append(
                [(app + '-CPU%SYS'), fault, jitter(app_fault_statistics.get_faulty_values('CPU', 'SYS'))])
            jitter_heatmap_data.append(
                [(app + '-CPU%USR'), fault, jitter(app_fault_statistics.get_faulty_values('CPU', 'USR'))])
            jitter_heatmap_data.append(
                [(app + '-MEM'), fault, jitter(app_fault_statistics.get_faulty_values('MEM', ''))])
            jitter_heatmap_data.append(
                [(app + '-DISK'), fault, jitter(app_fault_statistics.get_faulty_values('DISK', ''))])
            network_jitter_heatmap_date.append(
                [(app + '-NET-REC'), fault, jitter(app_fault_statistics.get_faulty_values('NET', 'REC'))])
            network_jitter_heatmap_date.append(
                [(app + '-NET-TRA'), fault, jitter(app_fault_statistics.get_faulty_values('NET', 'TRA'))])
            latency_jitter_data.append(
                [(app + '-LATENCY'), fault, jitter(app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME'))])
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
                                 utils.get_avg_without_outlier(
                                     app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME')),
                                 utils.get_std_without_outlier(
                                     app_fault_statistics.get_faulty_values('LATENCY', 'COM-TIME'))))

            if not no_fault_written:
                # jitter_heatmap_data.append([(app + '-CPU%SYS'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('CPU', 'SYS', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-CPU%USR'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('CPU', 'USR', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-MEM'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('MEM', '', is_faulty=False)])
                # jitter_heatmap_data.append([(app + '-DISK'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('DISK', '', is_faulty=False)])
                # network_jitter_heatmap_date.append([(app + '-NET-REC'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('NET', 'REC', is_faulty=False)])
                # network_jitter_heatmap_date.append([(app + '-NET-TRA'), 'No-Fault', app_fault_statistics.jitter_faulty_fault_free('NET', 'TRA', is_faulty=False)])

                jitter_heatmap_data.append(
                    [(app + '-CPU%SYS'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('CPU', 'SYS'))])
                jitter_heatmap_data.append(
                    [(app + '-CPU%USR'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('CPU', 'USR'))])
                jitter_heatmap_data.append(
                    [(app + '-MEM'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('MEM', ''))])
                jitter_heatmap_data.append(
                    [(app + '-DISK'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('DISK', ''))])
                network_jitter_heatmap_date.append(
                    [(app + '-NET-REC'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'REC'))])
                network_jitter_heatmap_date.append(
                    [(app + '-NET-TRA'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'TRA'))])
                latency_jitter_data.append([(app + '-LATENCY'), 'No-Fault',
                                            jitter(app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME'))])

                # jitter_heatmap_data.append([(app + '-NET-UTIL'), 'No-Fault', jitter(app_fault_statistics.get_fault_free_values('NET', 'UTIL'))])
                latency_data.append(((app + '-No-Fault'),
                                     utils.get_avg_without_outlier(
                                         app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME')),
                                     utils.get_std_without_outlier(
                                         app_fault_statistics.get_fault_free_values('LATENCY', 'COM-TIME'))))
                no_fault_written = True

    # draw_heatmap(x_labels, y_labels, jitter_heatmap_data)
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


if __name__ == '__main__':
    
    # app_fault_statistics = AppFaultStatistics('AE', 'CTXS-10000')
    # app_fault_statistics.plot_resource_with_residual('CPU', 'SYS', show_injection_times=False)
    # draw_fault_free_comparisons()
    app_statistic = AppStatistics('AE')

    # '2023-05-23 14:33:59.347000 - 2023-05-23 14:34:29.347000'
    # '2023-05-23 14:33:59.347000 - 2023-05-23 14:34:29.347000'
