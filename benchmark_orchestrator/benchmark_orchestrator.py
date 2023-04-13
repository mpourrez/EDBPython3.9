import csv

import configs
import utils
import grpc_client
import time
import analyze_results


####################################################################################
####################################################################################
## Saving latency and resource utilization results in csv file
####################################################################################
####################################################################################
def save_experiment_results(application, fault_config_file_name, results, res_utilizations):
    latency_filename = "./results/" + configs.EDGE_DEVICE_NAME + "/" + application + "-" + fault_config_file_name + \
                       ".csv"
    print("********[x]***** Saving results for filename:{}".format(latency_filename))
    print("********[x]***** Size of results: " + str(len(results)))
    with open(latency_filename, 'w', encoding='UTF8', newline='') as csv_output:
        # create the csv writer
        writer = csv.writer(csv_output)

        header = ['experiment_id', 'request_time_ms', 'request_received_time_ms', 'response_time_ms',
                  'response_received_time_ms', 'end_to_end_latency', 'compute_time', 'transmission_time', 'avg_cpu',
                  'avg_memory', 'avg_disk', 'avg_network', 'avg_power']
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
                   res_utilization.average_network_utilization, res_utilization.average_power_consumption]
            writer.writerow(row)


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
    if application == 'MM':
        grpc_result = client.call_matrix_multiplication()
    elif application == 'FFT':
        grpc_result = client.call_fast_fourier_transform()
    elif application == 'FPO-SIN':
        grpc_result = client.call_floating_point_sine()
    elif application == 'FPO-SQRT':
        grpc_result = client.call_floating_point_sqrt()
    elif application == 'SORT':
        grpc_result = client.call_sort_file()
    elif application == 'DD':
        grpc_result = client.call_dd_cmd()
    elif application == 'IPERF':
        grpc_result = client.call_iperf()
    elif application == 'IP':
        grpc_result = client.call_image_processing()
    elif application == 'SA':
        grpc_result = client.call_sentiment_analysis()
    elif application == 'ST':
        grpc_result = client.call_speech_to_text()
    elif application == 'IC-A-CPU':
        grpc_result = client.call_image_classification_alexnet_cpu()
    elif application == 'IC-S-CPU':
        grpc_result = client.call_image_classification_squeezenet_cpu()
    elif application == 'OD-CPU':
        grpc_result = client.call_object_detection_darknet()
    elif application == 'PS':
        grpc_result = client.call_pocket_sphinx()
    elif application == 'AE':
        grpc_result = client.call_aeneas()
    elif application == 'OT-CPU':
        grpc_result = client.call_object_tracking()

    response_received_time_ms = utils.current_milli_time()
    grpc_result.response_received_time_ms = response_received_time_ms
    resource_utilization_response = client.get_resource_utilization()
    return grpc_result, resource_utilization_response

####################################################################################
####################################################################################

if __name__ == '__main__':

    for edge_device_ip in configs.EDGE_DEVICES_IP:
        client = grpc_client.Client(edge_device_ip)
        for application in configs.APPLICATIONS:
            experiment_results = []
            resource_utilizations = []
            # Fault Free Experiments
            experiment_id = 1
            while experiment_id <= configs.REPEAT_EXPERIMENTS:
                exp_result, resource_utilization = run_single_experiment(client, application, None, None,
                                                                          experiment_id)
                experiment_results.append(exp_result)
                resource_utilizations.append(resource_utilization)
                experiment_id += 1

            print("********[x]***** Saving experiment results")
            save_experiment_results(application, "no-fault", experiment_results, resource_utilizations)

            # Experiments with Fault Injection
            for fault in configs.FAULTS:
                for fault_config in fault.fault_config:
                    experiment_results = []
                    resource_utilizations = []
                    experiment_id = 1
                    while experiment_id <= configs.REPEAT_EXPERIMENTS:
                        exp_result, resource_utilization = run_single_experiment(client, application, fault,
                                                                                 fault_config, experiment_id)
                        experiment_results.append(exp_result)
                        resource_utilizations.append(resource_utilization)
                        experiment_id += 1

                    print("********[x]***** Saving experiment results - with fault injections")
                    save_experiment_results(application, '{0}-{1}'.format(fault.abbreviation, fault_config),
                                            experiment_results, resource_utilizations)

            analyze_results.analyze_result_for_application(application, edge_device_ip)

