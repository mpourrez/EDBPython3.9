import grpc
from concurrent import futures
from protos import benchmark_pb2_grpc as pb2_grpc
from utils import *
from applications.object_tracking import object_tracker
from applications.object_detection import object_detector


class BenchmarkService(pb2_grpc.BenchmarksServicer):

    def __init__(self, *args, **kwargs):
        pass

    def track_objects(self, request, context):
        request_received_time_ms = current_milli_time()
        image = extract_image(request.image)
        tracking_result = object_tracker.track_from_image(image, request.frame_id, request.request_time_ms,
                                                          request_received_time_ms)
        return tracking_result

    def detect_objects(self, request, context):
        request_received_time_ms = current_milli_time()
        image = extract_image(request.image)
        detection_result = object_detector.detect_objects(image, request.frame_id, request.request_time_ms,
                                                          request_received_time_ms)
        return detection_result

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_BenchmarksServicer_to_server(BenchmarkService(), server)
    server.add_insecure_port('[::]:50051')
    print("Listening on Port 50051 ...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
