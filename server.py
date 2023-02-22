import grpc
from concurrent import futures
from base64 import b64decode
import cv2
import numpy as np
from protos import object_tracking_pb2_grpc as pb2_grpc
from protos import object_tracking_pb2 as pb2
from utils import *
from applications.object_tracking import object_tracker

class ObjectTrackingService(pb2_grpc.ObjectTrackingServicer):

    def __init__(self, *args, **kwargs):
        pass

    def track_objects(self, request, context):

        request_received_time_ms = current_milli_time()
        byte_array = bytearray(request.image, encoding='utf-8')
        decoded_bytes = b64decode(byte_array)
        numpy_array = np.frombuffer(decoded_bytes, np.uint8)
        image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
        tracking_result = object_tracker.track_from_image(image, request.frame_id, request.request_time_ms, request_received_time_ms)
        return tracking_result


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ObjectTrackingServicer_to_server(ObjectTrackingService(), server)
    server.add_insecure_port('[::]:50051')
    print("Listening on Port 50051 ...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()