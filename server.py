import grpc
from concurrent import futures
from protos import object_tracking_pb2_grpc as pb2_grpc
from protos import object_tracking_pb2 as pb2
from utils import *


class ObjectTrackingService(pb2_grpc.ObjectTrackingServicer):

    def __init__(self, *args, **kwargs):
        pass

    def track_objects(self, request, context):

        request_received_time_ms = current_milli_time()
        # image = request.image

        response_time_ms = current_milli_time()
        bounding_box = {'clazz': 'person', 'x_min': 12, 'x_max': 23, 'y_min': 34, 'y_max': 45}
        result = {
            'frame_id': request.frame_id,
            'request_time_ms': request.request_time_ms,
            'request_received_time_ms': request_received_time_ms,
            'response_time_ms': response_time_ms,
            'bounding_boxes':[bounding_box],
        }

        return pb2.TrackingResponse(**result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ObjectTrackingServicer_to_server(ObjectTrackingService(), server)
    server.add_insecure_port('[::]:50051')
    print("Listening on Port 50051 ...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()