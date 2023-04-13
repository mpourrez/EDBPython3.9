import grpc
from protos import benchmark_pb2_grpc as pb2_grpc
from protos import benchmark_pb2 as pb2
import subprocess
import time
import numpy as np

import configs
import utils

np.random.seed(1)


class Client(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, edge_device_ip):
        self.host = edge_device_ip
        self.server_port = configs.EDGE_DEVICE_PORT
        self.ping_process = None

        # instantiate a channel
        options = [('grpc.max_receive_message_length', 100 * 1024 * 1024)]
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port), options=options)

        # bind the client and the server
        self.application_stub = pb2_grpc.ApplicationBenchmarksStub(self.channel)
        self.micro_stub = pb2_grpc.MicroBenchmarksStub(self.channel)
        self.edge_resource_management_stub = pb2_grpc.EdgeResourceManagementStub(self.channel)

    def call_matrix_multiplication(self):
        matrix_size = 1080
        matrix_1 = np.random.rand(matrix_size, matrix_size)
        matrix_2 = np.random.rand(matrix_size, matrix_size)
        rows_1 = []
        rows_2 = []
        for i in range(matrix_1.shape[0]):
            row_1 = pb2.Row(values=list(matrix_1[i]))
            rows_1.append(row_1)
            row_2 = pb2.Row(values=list(matrix_2[i]))
            rows_2.append(row_2)
        grpc_matrix_1 = pb2.Matrix(rows=rows_1)
        grpc_matrix_2 = pb2.Matrix(rows=rows_2)
        request_time_ms = utils.current_milli_time()
        message = pb2.MatrixMultiplicationRequest(matrix_1=grpc_matrix_1, matrix_2=grpc_matrix_2,
                                                  request_time_ms=request_time_ms)
        return self.micro_stub.multiply_matrices(message)

    def call_fast_fourier_transform(self):
        input_sequence = np.random.rand(1000000)
        fourier_input = pb2.Row(values=list(input_sequence))
        request_time_ms = utils.current_milli_time()
        message = pb2.FastFourierRequest(input_sequence=fourier_input, request_time_ms=request_time_ms)
        return self.micro_stub.fast_fourier_transform(message)

    def call_floating_point_sine(self):
        floating_point_input = np.random.randint(1, 361)
        request_time_ms = utils.current_milli_time()
        message = pb2.FloatingPointRequest(floating_point_input=floating_point_input, request_time_ms=request_time_ms)
        return self.micro_stub.floating_point_sin(message)

    def call_floating_point_sqrt(self):
        floating_point_input = np.random.randint(10000, 30001)
        request_time_ms = utils.current_milli_time()
        message = pb2.FloatingPointRequest(floating_point_input=floating_point_input, request_time_ms=request_time_ms)
        return self.micro_stub.floating_point_sqrt(message)

    def call_sort_file(self):
        with open('../workloads/data.txt', "rb") as f:
            data = f.read()
        file_data = pb2.FileData()
        file_data.data = data
        request_time_ms = utils.current_milli_time()
        message = pb2.FileSorterRequest(file=file_data, request_time_ms=request_time_ms)
        return self.micro_stub.sort_file(message)

    def call_dd_cmd(self):
        request_time_ms = utils.current_milli_time()
        message = pb2.DDRequest(request_time_ms=request_time_ms)
        return self.micro_stub.dd_cmd(message)

    def call_iperf(self):
        request_time_ms = utils.current_milli_time()
        message = pb2.IperfRequest(hostname=configs.ORCHESTRATOR_IP, port=configs.EDGE_DEVICE_PORT, duration=3
                                   , request_time_ms=request_time_ms)
        return self.micro_stub.run_iperf(message)

    # END: Micor Benchmarks

    def call_edge_to_start_resource_tracing(self):
        empty = pb2.EmptyProto()
        return self.edge_resource_management_stub.start_resource_tracing(empty)

    def get_resource_utilization(self):
        empty = pb2.EmptyProto()
        return self.edge_resource_management_stub.get_resource_utilization(empty)

    def call_server_to_get_fault_injection_status(self):
        message = pb2.EmptyProto()
        return self.edge_resource_management_stub.get_fault_injection_status(message)

    def call_server_to_inject_fault(self, fault_command, fault_config):
        message = pb2.FaultRequest(fault_command=fault_command, fault_config=fault_config)
        return self.edge_resource_management_stub.inject_fault(message)

    # END RESOURCE MANAGEMENT CODES

    def call_image_processing(self):
        request_time_ms = utils.current_milli_time()
        image = utils.get_random_image()
        message = pb2.ImageProcessingRequest(image=image, request_time_ms=request_time_ms)
        return self.application_stub.image_processing(message)

    def call_sentiment_analysis(self):
        request_time_ms = utils.current_milli_time()
        input_text = utils.get_random_sentiment_text()
        message = pb2.SentimentAnalysisRequest(input_text=input_text, request_time_ms=request_time_ms)
        return self.application_stub.sentiment_analysis(message)

    def call_speech_to_text(self):
        request_time_ms = utils.current_milli_time()
        audio = utils.get_random_audio()
        message = pb2.SpeechToTextRequest(audio=audio, request_time_ms=request_time_ms)
        return self.application_stub.speech_to_text(message)
    def call_image_classification_alexnet_cpu(self):
        request_time_ms = utils.current_milli_time()
        image = utils.get_random_image()
        message = pb2.ImageClassificationRequest(image=image, request_time_ms=request_time_ms)
        return self.application_stub.image_classification_alexnet(message)

    def call_image_classification_squeezenet_cpu(self):
        request_time_ms = utils.current_milli_time()
        image = utils.get_random_image()
        message = pb2.ImageClassificationRequest(image=image, request_time_ms=request_time_ms)
        return self.application_stub.image_classification_squeezenet(message)

    def call_object_detection_darknet(self):
        request_time_ms = utils.current_milli_time()
        image = utils.get_random_image()
        message = pb2.ObjectDetectionRequest(image=image, request_time_ms=request_time_ms)
        return self.application_stub.object_detection_darknet(message)

    def call_pocket_sphinx(self):
        request_time_ms = utils.current_milli_time()
        audio = utils.get_random_audio()
        message = pb2.PocketSphinxRequest(audio=audio, request_time_ms=request_time_ms)
        return self.application_stub.pocket_sphinx(message)

    def call_aeneas(self):
        request_time_ms = utils.current_milli_time()
        audio, transcript = utils.get_random_audio_text_for_alignment()
        message = pb2.AudioTextRequest(audio=audio, text_input=transcript, request_time_ms=request_time_ms)
        return self.application_stub.pocket_sphinx(message)

    def call_object_tracking(self):
        request_time_ms = utils.current_milli_time()
        image = utils.get_random_image_for_tracking()
        message = pb2.ObjectTrackingRequest(image=image, request_time_ms=request_time_ms)
        return self.application_stub.object_tracking(message)

    ######################################################
    ############ OLD CODE:################################
    ######################################################

    def call_object_tracking_server(self, image, frame_id):
        message = create_grpc_request(image, frame_id)
        return self.application_stub.track_objects(message)

    def call_object_detection_server(self, image, frame_id):
        message = create_grpc_request(image, frame_id)
        return self.application_stub.detect_objects(message)

    def call_pocketsphinx(self, audio, frame_id):
        message = create_grpc_request(audio, frame_id)
        return self.application_stub.speech_to_text(message)

    # def call_aeneas(self, audio, text_input, frame_id):
    #     request_time_ms = utils.current_milli_time()
    #     message = pb2.AudioTextRequest(audio=audio, text_input=text_input, frame_id=frame_id,
    #                                    request_time_ms=request_time_ms)
    #     return self.application_stub.align_speech_text(message)

    def call_server_to_start_mem_tracing(self):
        empty = pb2.EmptyProto()
        return self.application_stub.start_memory_tracing(empty)

    def call_server_for_cpu_trace(self):
        empty = pb2.EmptyProto()
        return self.application_stub.get_cpu_trace(empty)

    def call_server_for_memory_trace(self):
        empty = pb2.EmptyProto()
        return self.application_stub.get_memory_usage(empty)



    # def call_server_to_get_fault_injection_status(self):
    #     message = pb2.EmptyProto()
    #     return self.application_stub.get_fault_injection_status(message)
    #
    # def ping_flood_edge_device(self, command, config):
    #     shell_command = '{0} {1}'.format(command, config)
    #     print('[x] TCP flooding the edge device: ' + shell_command)
    #     self.ping_process = subprocess.Popen(shell_command, shell=True)
    #     # wait for the subprocess to start the job
    #     time.sleep(10)
    #
    # def kill_ping_process(self):
    #     print("killing process!!!")
    #     self.ping_process.kill()
    #     # wait for kill process to finish
    #     time.sleep(10)
    #     if self.ping_process.poll() is None:
    #         return False
    #     return True


####################################################################################
####################### Create a gRPC request ######################################
####################################################################################
def create_grpc_request(image, frame_id):
    request_time_ms = utils.current_milli_time()
    message = pb2.Request(image=image, frame_id=frame_id, request_time_ms=request_time_ms)
    return message
