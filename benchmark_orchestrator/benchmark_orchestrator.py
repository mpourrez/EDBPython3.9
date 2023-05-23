import sys

sys.path.append('..')
import csv

import configs
import utils
import grpc_client
import time
import analyze_results
import multiprocessing
import benchmark_orchestrator
import os
import signal


####################################################################################
####################################################################################
## Saving latency and resource utilization results in csv file
####################################################################################
####################################################################################
def save_experiment_results_over_time(application, fault_config_file_name, results):
    latency_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application \
                       + "-" + fault_config_file_name + "-Latency.csv"
    print("********[x]***** Saving results for filename:{}".format(latency_filename))
    print("********[x]***** Size of results: " + str(len(results)))
    with open(latency_filename, 'w', encoding='UTF8', newline='') as csv_output:
        # create the csv writer
        writer = csv.writer(csv_output)

        header = ['request_number', 'request_time_ms', 'request_received_time_ms', 'response_time_ms',
                  'response_received_time_ms', 'end_to_end_latency', 'compute_time', 'transmission_time']
        writer.writerow(header)
        index = 0
        for result in results:
            index += 1
            end_to_end_latency = result.response_received_time_ms - result.request_time_ms
            compute_time = result.response_time_ms - result.request_received_time_ms
            transmission_time = end_to_end_latency - compute_time
            row = [index, result.request_time_ms, result.request_received_time_ms,
                   result.response_time_ms, result.response_received_time_ms, end_to_end_latency,
                   compute_time, transmission_time]
            writer.writerow(row)


def save_experiment_results(application, fault_config_file_name, results, res_utilizations):
    latency_filename = configs.PROJECT_PATH + "EDB/results/" + configs.EDGE_DEVICE_NAME + "/" + application + "-" + \
                       fault_config_file_name + ".csv"
    print("********[x]***** Saving results for filename:{}".format(latency_filename))
    print("********[x]***** Size of results: " + str(len(results)))
    with open(latency_filename, 'w', encoding='UTF8', newline='') as csv_output:
        # create the csv writer
        writer = csv.writer(csv_output)

        header = ['experiment_id', 'request_time_ms', 'request_received_time_ms', 'response_time_ms',
                  'response_received_time_ms', 'end_to_end_latency', 'compute_time', 'transmission_time', 'avg_cpu',
                  'avg_memory', 'avg_disk', 'avg_network_received_sp', 'avg_network_transmitted_sp', 'avg_temperature']
        writer.writerow(header)
        index = 0
        for result in results:
            res_utilization = res_utilizations[index]
            index += 1
            end_to_end_latency = result.response_received_time_ms - result.request_time_ms
            compute_time = result.response_time_ms - result.request_received_time_ms
            transmission_time = end_to_end_latency - compute_time
            row = [index, result.request_time_ms, result.request_received_time_ms,
                   result.response_time_ms, result.response_received_time_ms, end_to_end_latency,
                   compute_time, transmission_time, res_utilization.average_cpu_utilization,
                   res_utilization.average_memory_utilization, res_utilization.average_disk_utilization,
                   res_utilization.average_network_received_speed, res_utilization.average_network_transmitted_speed,
                   res_utilization.average_power_consumption]
            writer.writerow(row)


def save_resource_logs(application, fault_config_file_name, resource_logs):
    cpu_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application + \
                   "-" + fault_config_file_name + "-CPU.txt"
    mem_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application + \
                   "-" + fault_config_file_name + "-MEM.txt"
    net_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application + \
                   "-" + fault_config_file_name + "-NET.txt"
    io_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application + \
                  "-" + fault_config_file_name + "-IO.txt"
    cpu_temps_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + application + \
                         "-" + fault_config_file_name + "-TEMP.txt"
    fault_injection_filename = configs.PROJECT_PATH + "EDB/results_over_time/" + configs.EDGE_DEVICE_NAME + "/" + \
                               application + "-" + fault_config_file_name + "-FaultInjection.csv"
    with open(cpu_filename, "wb") as cpu_f:
        cpu_f.write(resource_logs.cpu_log.data)

    with open(mem_filename, "wb") as mem_f:
        mem_f.write(resource_logs.memory_log.data)

    with open(net_filename, "wb") as net_f:
        net_f.write(resource_logs.network_log.data)

    with open(io_filename, "wb") as io_f:
        io_f.write(resource_logs.io_log.data)

    with open(cpu_temps_filename, 'w', encoding='UTF8', newline='') as temp_csv_output:
        # create the csv writer
        temp_writer = csv.writer(temp_csv_output)
        temp_writer.writerow(["Timestamp_ms", "CPU_Temp"])
        for t_time, cpu_t in zip(resource_logs.temperature_timestamps_ms, resource_logs.cpu_temperatures):
            temp_writer.writerow([t_time, cpu_t])

    with open(fault_injection_filename, 'w', encoding='UTF8', newline='') as fi_csv_output:
        fi_writer = csv.writer(fi_csv_output)

        fi_writer.writerow(["fault_injection_start_time", "fault_injection_stop_time"])
        for f_start, f_stop in zip(resource_logs.fault_injection_start_times_ms,
                                   resource_logs.fault_injection_stop_times_ms):
            fi_writer.writerow([f_start, f_stop])


####################################################################################
####################################################################################
####################################################################################
####################################################################################
def run_single_experiment(client, application, fault, fault_config, experiment_id):
    fault_config_file_name = 'no-fault'
    if fault is not None:
        fault_config_file_name = '{0}-{1}'.format(fault.abbreviation, fault_config)
    print("***************************************************************************************")
    print("****************** Starting experiment: device:{0} - ip:{1} - app:{2} - {3} - exp id: {4}".format(
        configs.EDGE_DEVICE_NAME, client.host, application, fault_config_file_name, experiment_id))
    print("***************************************************************************************")

    fault_injection_status = client.call_server_to_get_fault_injection_status()
    while not fault_injection_status.is_finished:
        print("[x] Previous experiment still in progress, we need to wait!! - (fault injection in progress)")
        time.sleep(3)
        fault_injection_status = client.call_server_to_get_fault_injection_status()
    print("********[x]***** Ready to start the experiment.")
    client.call_edge_to_start_resource_tracing()
    if fault is not None and fault.abbreviation != 'TCP' and fault.abbreviation != 'PING':
        client.call_server_to_inject_fault(fault.fault_command, fault_config)
    time.sleep(configs.TIME_BOUND_FOR_FAULT_INJECTION)  ### Sleep a bit until stressors are ready to go

    # **** Starting the experiment ****************** #
    grpc_result = get_application_result(application)
    resource_utilization_response = client.get_resource_utilization()
    return grpc_result, resource_utilization_response


####################################################################################
####################################################################################
def get_application_result(application_to_test):
    if application_to_test == 'MM':
        grpc_result = client.call_matrix_multiplication()
    elif application_to_test == 'FFT':
        grpc_result = client.call_fast_fourier_transform()
    elif application_to_test == 'FPO-SIN':
        grpc_result = client.call_floating_point_sine()
    elif application_to_test == 'FPO-SQRT':
        grpc_result = client.call_floating_point_sqrt()
    elif application_to_test == 'SORT':
        grpc_result = client.call_sort_file()
    elif application_to_test == 'DD':
        grpc_result = client.call_dd_cmd()
    elif application_to_test == 'IPERF':
        grpc_result = client.call_iperf()
    elif application_to_test == 'IP':
        grpc_result = client.call_image_processing()
    elif application_to_test == 'SA':
        grpc_result = client.call_sentiment_analysis()
    elif application_to_test == 'ST':
        grpc_result = client.call_speech_to_text()
    elif application_to_test == 'IC-A-CPU':
        grpc_result = client.call_image_classification_alexnet_cpu()
    elif application_to_test == 'IC-S-CPU':
        grpc_result = client.call_image_classification_squeezenet_cpu()
    elif application_to_test == 'OD-CPU':
        grpc_result = client.call_object_detection_darknet()
    elif application_to_test == 'PS':
        grpc_result = client.call_pocket_sphinx()
    elif application_to_test == 'AE':
        grpc_result = client.call_aeneas()
    elif application_to_test == 'OT-CPU':
        grpc_result = client.call_object_tracking()
    if grpc_result:
        response_received_time_ms = utils.current_milli_time()
        grpc_result.response_received_time_ms = response_received_time_ms
        print("[x] Received Result of Application Call {0}".format(application_to_test))
    return grpc_result


####################################################################################
####################################################################################
def run_application_over_time_fault_free(edge_server, application_to_test):
    print("***************************************************************************************")
    print("****************** Starting experiment: device:{0} - ip:{1} - app:{2} - Fault - Free".format(
        configs.EDGE_DEVICE_NAME, edge_server.host, application_to_test))
    print("***************************************************************************************")
    resource_tracing_status = client.call_server_to_get_resource_tracking_status()
    while not resource_tracing_status.is_finished:
        print("[x] Previous experiment still in progress, we need to wait!! - (resource monitoring in progress)")
        time.sleep(3)
        resource_tracing_status = client.call_server_to_get_resource_tracking_status()
    edge_server.call_edge_to_start_resource_tracing_with_saving()

    exp_results = []

    print("[x]**** Start Fault Free Operations")
    configs.EXPERIMENT_DURATION = 4 * configs.FAULT_FREE_DURATIONS
    start_time = time.time()
    while time.time() < start_time + configs.EXPERIMENT_DURATION:
        grpc_result = get_application_result(application_to_test)
        if grpc_result:
            exp_results.append(grpc_result)
    print("[x]**** End Fault Free Operations")
    return exp_results

def run_application_over_time(edge_server, application_to_test, fault_to_inject, fconfig):
    print("***************************************************************************************")
    print("****************** Starting experiment: device:{0} - ip:{1} - app:{2} - fault:{3} - config:{4}".format(
        configs.EDGE_DEVICE_NAME, edge_server.host, application_to_test, fault_to_inject.abbreviation, fconfig))
    print("***************************************************************************************")
    # resource_tracing_status = client.call_server_to_get_resource_tracking_status()
    # while not resource_tracing_status.is_finished:
    #     print("[x] Previous experiment still in progress, we need to wait!! - (fault injection in progress)")
    #     time.sleep(3)
    #     resource_tracing_status = client.call_server_to_get_resource_tracking_status()

    edge_server.call_edge_to_start_resource_tracing_with_saving()

    exp_results = []

    injected_faults_count = 0
    while injected_faults_count < configs.NUMBER_OF_FAULT_INJECTIONS:
        print("[x]**** Start Fault Free Operations")
        start_time = time.time()
        while time.time() < start_time + configs.FAULT_FREE_DURATIONS:
            grpc_result = get_application_result(application_to_test)
            if grpc_result:
                exp_results.append(grpc_result)
        print("[x]**** End Fault Free Operations")
        edge_server.call_server_to_inject_fault(fault_to_inject.fault_command, fconfig)
        print("[x]**** Start Faultyyyyy Operations")
        start_time = time.time()
        while time.time() < start_time + configs.FAULT_INJECTION_DURATION:
            grpc_result = get_application_result(application_to_test)
            if grpc_result:
                exp_results.append(grpc_result)
        print("[x]**** End Faultyyyyy Operations")
        # edge_server.call_server_to_stop_fault_injection()
        fault_injection_status = client.call_server_to_get_fault_injection_status()
        while not fault_injection_status.is_finished:
            print("[x] Previous experiment still in progress, we need to wait!! - (fault injection in progress)")
            time.sleep(3)
            fault_injection_status = client.call_server_to_get_fault_injection_status()
        injected_faults_count += 1

    print("[x]**** Start Fault Free Operations")
    start_time = time.time()
    while time.time() < start_time + configs.FAULT_FREE_DURATIONS:
        grpc_result = get_application_result(application_to_test)
        if grpc_result:
            exp_results.append(grpc_result)
    print("[x]**** End Fault Free Operations")
    return exp_results

    # sent_fault_request = False
    # while time.time() < start_time + configs.MAX_EXPERIMENT_TIME:
    #     if not sent_fault_request and time.time() > start_time + configs.FAULT_FREE_DURATIONS:
    #         edge_server.call_server_to_inject_fault(fault_to_inject.fault_command, fconfig)
    #         sent_fault_request = True
    #     grpc_result = get_application_result(application_to_test)
    #     if grpc_result:
    #         exp_results.append(grpc_result)
    #


####################################################################################
####################################################################################

if __name__ == '__main__':
    utils.initial_workload_setup()
    for edge_device_ip in configs.EDGE_DEVICES_IP:
        client = grpc_client.Client(edge_device_ip)
        for app in configs.APPLICATIONS:
            ######################################################################
            ####### Fault Free Resource Evaluations ##############################
            experiment_results = run_application_over_time_fault_free(client, app)
            time.sleep(10)
            save_experiment_results_over_time(app, 'No-Fault', experiment_results)
            resource_logs = client.get_resource_logs()
            save_resource_logs(app, 'No-Fault', resource_logs)
            ######################################################################

        for app in configs.APPLICATIONS:
            for fault in configs.FAULTS:
                for fault_config in fault.fault_config:
                    experiment_results = run_application_over_time(client, app, fault, fault_config)
                    time.sleep(10)
                    save_experiment_results_over_time(app, '{0}-{1}'.format(fault.abbreviation, fault_config),
                                                      experiment_results)
                    resource_logs = client.get_resource_logs()
                    save_resource_logs(app, '{0}-{1}'.format(fault.abbreviation, fault_config), resource_logs)


            ################################################################################
            ################################################################################
            ################################################################################

            # experiment_results = []
            # resource_utilizations = []
            # # Fault Free Experiments
            # experiment_id = 1
            # while experiment_id <= configs.REPEAT_EXPERIMENTS:
            #     exp_result, resource_utilization = run_single_experiment(client, application, None, None,
            #                                                               experiment_id)
            #     experiment_results.append(exp_result)
            #     resource_utilizations.append(resource_utilization)
            #     experiment_id += 1
            #
            # print("********[x]***** Saving experiment results")
            # save_experiment_results(application, "no-fault", experiment_results, resource_utilizations)

            # Experiments with Fault Injection
            # for fault in configs.FAULTS:
            #     for fault_config in fault.fault_config:
            #         experiment_results = []
            #         resource_utilizations = []
            #         experiment_id = 1
            #         while experiment_id <= configs.REPEAT_EXPERIMENTS:
            #             exp_result, resource_utilization = run_single_experiment(client, application, fault,
            #                                                                      fault_config, experiment_id)
            #             experiment_results.append(exp_result)
            #             resource_utilizations.append(resource_utilization)
            #             experiment_id += 1
            #
            #         print("********[x]***** Saving experiment results - with fault injections")
            #         save_experiment_results(application, '{0}-{1}'.format(fault.abbreviation, fault_config),
            #                                 experiment_results, resource_utilizations)
            #
            # analyze_results.analyze_result_for_application(application, edge_device_ip)
