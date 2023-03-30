import configs
import csv
from scipy import stats
import numpy as np
from pathlib import Path
import math

avg_response_times = []
avg_compute_times = []
avg_transmission_times = []
num_transmitted_frames = []
cpu_usages = []
memory_usages = []

std_response_times = []
std_compute_times = []
std_transmission_times = []

def calculate_standard_dev(values):
    a = 1.0 * np.array(values)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + 0.95) / 2., n - 1)
    return h

def find_latency_without_outliers(filename):
    print("[x] Summarizing Latencies for file: {}".format(filename))
    latency_file_rows = []
    response_times = []
    compute_times = []
    transmission_times = []

    avg_response_time = 0
    avg_compute_time = 0
    avg_transmission_time = 0

    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        row_number = 1
        for row in csvreader:
            latency_file_rows.append(row)
            if len(row)<5:
                # We reached end of file to the cpu and mem utilization
                break
            response_times.append(int(row[5]))
            compute_times.append(int(row[6]))
            transmission_times.append(int(row[7]))
            row_number += 1

        # get cpu and memory usage values from the file
        resource_utilization = next(csvreader)
        cpu_usage = float(resource_utilization[0])
        cpu_usages.append(cpu_usage)
        memory_usage = float(resource_utilization[1])
        memory_usages.append(memory_usage)
        num_transmitted_frames.append(row_number)

        # Finding outliers in one-way-latencies
        z = np.abs(stats.zscore(response_times))
        response_times_without_outliers = []
        compute_times_without_outliers = []
        transmission_times_without_outliers = []
        count_non_outliers1 = 0
        for i in range(0, len(response_times)):
            if (z[i] > -3 and z[i] < 3) or math.isnan(z[i]) :
                response_times_without_outliers.append(response_times[i])
                compute_times_without_outliers.append(compute_times[i])
                transmission_times_without_outliers.append(transmission_times[i])
                avg_response_time += response_times[i]
                avg_compute_time += compute_times[i]
                avg_transmission_time += transmission_times[i]
                count_non_outliers1 += 1
            else:
                print("This is outlier: {}".format(response_times[i]))

        avg_response_time /= count_non_outliers1
        avg_compute_time /= count_non_outliers1
        avg_transmission_time /= count_non_outliers1

        avg_response_times.append(avg_response_time)
        avg_compute_times.append(avg_compute_time)
        avg_transmission_times.append(avg_transmission_time)

        std_response_times.append(calculate_standard_dev(response_times_without_outliers))
        std_compute_times.append(calculate_standard_dev(compute_times_without_outliers))
        std_transmission_times.append(calculate_standard_dev(transmission_times_without_outliers))


def add_csv_headers_for_experiment(csv_writer):
    header = []
    ################### Experiment Info #########################
    header.append('application')
    header.append('fault')
    header.append('config')
    header.append('test_num')
    #############################################################

    ################# Latency Results Headers ###################
    header.append('transmitted_frames')
    header.append('avg_response_time')
    header.append('avg_compute_time')
    header.append('avg_transmission_time')
    header.append('average_cpu_load_percent')
    header.append('peak_memory_usage_MB')
    csv_writer.writerow(header)

def add_csv_headers_for_final_summary(csv_writer):
    header = []
    ################### Experiment Info #########################
    header.append('application')
    header.append('device')
    header.append('fault')
    header.append('config')
    #############################################################

    ################# Latency Results Headers ###################
    header.append('avg_transmitted_frames')
    header.append('avg_response_time')
    header.append('avg_compute_time')
    header.append('avg_transmission_time')
    header.append('avg_cpu_load_percent')
    header.append('avg_peak_memory_usage_MB')

    header.append('std_transmitted_frames')
    header.append('std_response_time')
    header.append('std_compute_time')
    header.append('std_transmission_time')
    header.append('std_cpu_utilization')
    header.append('std_memory_utilization')
    csv_writer.writerow(header)

def add_row_final_summary(csvwriter, application, device_name, fault, config):
    row = []
    row.append(application)
    row.append(device_name)
    row.append(fault)
    row.append(config)

    row.append("{0:.1f}".format(get_avg_without_outlier(num_transmitted_frames)))
    row.append("{0:.3f}".format(get_avg_without_outlier(avg_response_times)))
    row.append("{0:.3f}".format(get_avg_without_outlier(avg_compute_times)))
    row.append("{0:.3f}".format(get_avg_without_outlier(avg_transmission_times)))
    row.append("{0:.3f}".format(get_avg_without_outlier(cpu_usages)))
    row.append("{0:.3f}".format(get_avg_without_outlier(memory_usages)))

    row.append("{0:.1f}".format(get_std_without_outlier(num_transmitted_frames)))
    row.append("{0:.3f}".format(get_std_without_outlier(avg_response_times)))
    row.append("{0:.3f}".format(get_std_without_outlier(avg_compute_times)))
    row.append("{0:.3f}".format(get_std_without_outlier(avg_transmission_times)))
    row.append("{0:.3f}".format(get_std_without_outlier(cpu_usages)))
    row.append("{0:.3f}".format(get_std_without_outlier(memory_usages)))
    csvwriter.writerow(row)


def add_summary_row(csvwriter, application, fault, config, experiment_id):
    row = []
    row.append(application)
    row.append(fault)
    row.append(config)
    row.append(experiment_id)

    row.append(num_transmitted_frames[experiment_id-1])
    row.append(avg_response_times[experiment_id-1])
    row.append(avg_compute_times[experiment_id-1])
    row.append(avg_transmission_times[experiment_id-1])
    row.append(cpu_usages[experiment_id-1])
    row.append(memory_usages[experiment_id-1])
    csvwriter.writerow(row)

def clear_fields():
    global num_transmitted_frames, avg_response_times, avg_transmission_times, avg_compute_times, cpu_usages, memory_usages

    num_transmitted_frames = []
    avg_response_times = []
    avg_compute_times = []
    avg_transmission_times = []
    cpu_usages = []
    memory_usages = []

def analyze_each_experiment():
    for application in configs.APPLICATIONS:
        with open('results3/latency/summaries/' + application + '-raspberrypi-no-fault-summary.csv', 'w', encoding='UTF8',
                  newline='') as csv_output:
            writer = csv.writer(csv_output)
            experiment_id = 1
            add_csv_headers_for_experiment(writer)
            while experiment_id <= configs.REPEAT_EXPERIMENTS:
                # clear_fields()
                print("**********experiment id: {}".format(experiment_id))
                result_latency_filename = 'results3/latency/' + application + '/raspberrypi-no-fault-exp' +str(experiment_id)+ ".csv"
                find_latency_without_outliers(result_latency_filename)
                add_summary_row(writer, application, 'no-fault', '-', experiment_id)
                experiment_id += 1

        for fault in configs.FAULTS:
            for fault_config in fault.fault_config:
                with open('results3/latency/summaries/' + application + '-raspberrypi-' + fault.abbreviation + '-' + fault_config +'-summary.csv', 'w', encoding='UTF8',
                          newline='') as csv_output:
                    writer = csv.writer(csv_output)
                    experiment_id = 1
                    add_csv_headers_for_experiment(writer)
                    clear_fields()
                    while experiment_id <= configs.REPEAT_EXPERIMENTS:
                        print("**********experiment id: {}".format(experiment_id))
                        result_latency_filename = 'results3/latency/' + application + '/raspberrypi-' + \
                                                  fault.abbreviation + '-' + fault_config +'-exp' + str(experiment_id) + ".csv"
                        if Path(result_latency_filename).is_file():
                            find_latency_without_outliers(result_latency_filename)
                            add_summary_row(writer, application, fault.abbreviation, fault_config, experiment_id)
                        experiment_id += 1

def analyze_result_for_application(application):
    with open('results4/latency/summaries/' + application + '-raspberrypi-no-fault-summary.csv', 'w', encoding='UTF8',
              newline='') as csv_output:
        writer = csv.writer(csv_output)
        experiment_id = 1
        add_csv_headers_for_experiment(writer)
        while experiment_id <= configs.REPEAT_EXPERIMENTS:
            # clear_fields()
            print("**********experiment id: {}".format(experiment_id))
            result_latency_filename = 'results4/latency/' + application + '/raspberrypi-no-fault-exp' + str(
                experiment_id) + ".csv"
            find_latency_without_outliers(result_latency_filename)
            add_summary_row(writer, application, 'no-fault', '-', experiment_id)
            experiment_id += 1

    for fault in configs.FAULTS:
        for fault_config in fault.fault_config:
            with open(
                    'results4/latency/summaries/' + application + '-raspberrypi-' + fault.abbreviation + '-' + fault_config + '-summary.csv',
                    'w', encoding='UTF8',
                    newline='') as csv_output:
                writer = csv.writer(csv_output)
                experiment_id = 1
                add_csv_headers_for_experiment(writer)
                clear_fields()
                while experiment_id <= configs.REPEAT_EXPERIMENTS:
                    print("**********experiment id: {}".format(experiment_id))
                    result_latency_filename = 'results4/latency/' + application + '/raspberrypi-' + \
                                              fault.abbreviation + '-' + fault_config + '-exp' + str(
                        experiment_id) + ".csv"
                    if Path(result_latency_filename).is_file():
                        find_latency_without_outliers(result_latency_filename)
                        add_summary_row(writer, application, fault.abbreviation, fault_config, experiment_id)
                    experiment_id += 1

def get_avg_without_outlier(data_list):
    if np.std(data_list) == 0:
        return sum(data_list)/len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    for i in range(0, len(data_list)):
        if z[i]>-3 and z[i]<3:
            avg += data_list[i]
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))
    return avg/count

def get_std_without_outlier(data_list):
    if np.std(data_list) == 0:
        return sum(data_list)/len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    list_without_outliers = []
    for i in range(0, len(data_list)):
        if z[i]>-3 and z[i]<3:
            list_without_outliers.append(data_list[i])
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))

    a = 1.0 * np.array(list_without_outliers)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + 0.95) / 2., n - 1)
    return h

def extract_summary_result(file):
    global num_transmitted_frames, avg_response_times, avg_transmission_times, avg_compute_times, cpu_usages, memory_usages

    clear_fields()
    with open(file, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        test_num = 0
        for row in csvreader:
            num_transmitted_frames.append(int(row[4]))
            avg_response_times.append(float(row[5]))
            avg_compute_times.append(float(row[6]))
            avg_transmission_times.append(float(row[7]))
            cpu_usages.append(float(row[8]))
            memory_usages.append(float(row[9]))

if __name__ == '__main__':
    analyze_each_experiment()
    # with open('results3/ALL-Summary.csv', 'w', encoding='UTF8',
    #           newline='') as csv_output:
    #     writer = csv.writer(csv_output)
    #     add_csv_headers_for_final_summary(writer)
    #     for application in configs.APPLICATIONS:
    #         for device_name in ['raspberrypi']:
    #             no_fault_summary = 'results3/latency/summaries/' + application + "-" + device_name +\
    #                                '-no-fault-summary.csv'
    #             extract_summary_result(no_fault_summary)
    #             add_row_final_summary(writer, application, device_name, 'no-fault', '-')
    #
    #             for fault in configs.FAULTS:
    #                for fault_config in fault.fault_config:
    #                      fault_summary = 'results3/latency/summaries/' + application + "-" + device_name + \
    #                                         '-' + fault.abbreviation + '-' + fault_config + '-summary.csv'
    #                      extract_summary_result(fault_summary)
    #                      add_row_final_summary(writer, application, device_name, fault.abbreviation, fault_config)




