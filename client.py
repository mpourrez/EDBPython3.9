import grpc
from protos import object_tracking_pb2_grpc as pb2_grpc
from protos import object_tracking_pb2 as pb2
import cv2
from base64 import b64encode
from utils import *


class Client(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = 'localhost'
        self.server_port = 50051

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.ObjectTrackingStub(self.channel)

    def call_tracking_server(self, image):
        """
        Client function to call the rpc for track_objects
        """
        print("Calling the server ...")
        frame_id = 123
        request_time_ms = current_milli_time()
        message = pb2.Request(image=image, frame_id = frame_id, request_time_ms = request_time_ms)
        return self.stub.track_objects(message)


if __name__ == '__main__':
    client = Client()
    # Sample image as input
    im = cv2.imread('sampleimg.jpeg')
    ret, buffer = cv2.imencode('.jpg', im)
    jpg_as_text = b64encode(buffer)
    base64_string = jpg_as_text.decode('utf-8')

    # Make gRPC call
    result = client.call_tracking_server(image=base64_string)
    print(result)