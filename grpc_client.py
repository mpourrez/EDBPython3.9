import grpc
from protos import benchmark_pb2_grpc as pb2_grpc
from protos import benchmark_pb2 as pb2

import constants
import utils


class Client(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = constants.EDGE_DEVICE_IP
        self.server_port = constants.EDGE_DEVICE_PORT

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

    def call_server_to_start_mem_tracing(self):
        empty = pb2.EmptyProto()
        return self.stub.start_memory_tracing(empty)

    def call_server_for_cpu_trace(self):
        empty = pb2.EmptyProto()
        return self.stub.get_cpu_trace(empty)

    def call_server_for_memory_trace(self):
        empty = pb2.EmptyProto()
        return self.stub.get_memory_usage(empty)

####################################################################################
####################### Create a gRPC request ######################################
####################################################################################
def create_grpc_request(image, frame_id):
    request_time_ms = utils.current_milli_time()
    message = pb2.Request(image=image, frame_id=frame_id, request_time_ms=request_time_ms)
    return message
