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


####################################################################################
####################### Create a gRPC request ######################################
####################################################################################
def create_grpc_request(image, frame_id):
    request_time_ms = utils.current_milli_time()
    message = pb2.Request(image=image, frame_id=frame_id, request_time_ms=request_time_ms)
    return message
