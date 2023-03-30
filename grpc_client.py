import grpc
from protos import benchmark_pb2_grpc as pb2_grpc
from protos import benchmark_pb2 as pb2
import subprocess
import time

import configs
import utils


class Client(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = configs.EDGE_DEVICE_IP
        self.server_port = configs.EDGE_DEVICE_PORT
        self.ping_process = None

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.BenchmarksStub(self.channel)

    def call_object_tracking_server(self, image, frame_id):
        message = create_grpc_request(image, frame_id)
        return self.stub.track_objects(message)

    def call_object_detection_server(self, image, frame_id):
        message = create_grpc_request(image, frame_id)
        return self.stub.detect_objects(message)

    def call_pocketsphinx(self, audio, frame_id):
        message = create_grpc_request(audio, frame_id)
        return self.stub.speech_to_text(message)

    def call_aeneas(self, audio, text_input, frame_id):
        request_time_ms = utils.current_milli_time()
        message = pb2.AudioTextRequest(audio=audio, text_input=text_input, frame_id=frame_id,
                                       request_time_ms=request_time_ms)
        return self.stub.align_speech_text(message)

    def call_server_to_start_mem_tracing(self):
        empty = pb2.EmptyProto()
        return self.stub.start_memory_tracing(empty)

    def call_server_for_cpu_trace(self):
        empty = pb2.EmptyProto()
        return self.stub.get_cpu_trace(empty)

    def call_server_for_memory_trace(self):
        empty = pb2.EmptyProto()
        return self.stub.get_memory_usage(empty)

    def call_server_to_inject_fault(self, fault_command, fault_config, time):
        message = pb2.FaultRequest(fault_command=fault_command, fault_config=fault_config, timeout=time)
        return self.stub.inject_fault(message)

    def call_server_to_get_fault_injection_status(self):
        message = pb2.EmptyProto()
        return self.stub.get_fault_injection_status(message)

    def ping_flood_edge_device(self, command, config):
        shell_command = '{0} {1}'.format(command, config)
        print('[x] TCP flooding the edge device: ' + shell_command)
        self.ping_process = subprocess.Popen(shell_command, shell=True)
        # wait for the subprocess to start the job
        time.sleep(10)

    def kill_ping_process(self):
        print("killing process!!!")
        self.ping_process.kill()
        # wait for kill process to finish
        time.sleep(10)
        if self.ping_process.poll() is None:
            return False
        return True

####################################################################################
####################### Create a gRPC request ######################################
####################################################################################
def create_grpc_request(image, frame_id):
    request_time_ms = utils.current_milli_time()
    message = pb2.Request(image=image, frame_id=frame_id, request_time_ms=request_time_ms)
    return message
