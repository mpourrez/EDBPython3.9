from utils import *
from protos import benchmark_pb2_grpc as pb2_grpc

class ApplicationBenchmarksGRPCService(pb2_grpc.ApplicationBenchmarksServicer):

    def __init__(self, *args, **kwargs):
        self.fault_injection_process = None
        self.utilization_output = None
        self.resource_tracing_process = None

    def image_processing(self, request, context):
        return request

    def sentiment_analysis(self, request, context):
        return request

    def speech_to_text(self, request, context):
        return request

    def image_classification_alexnet(self, request, context):
        return request

    def image_classification_alexnet_gpu(self, request, context):
        return request

    def image_classification_squeezenet(self, request, context):
        return request

    def image_classification_squeezenet_gpu(self, request, context):
        return request

    def object_detection_darknet(self, request, context):
        return request

    def object_detection_darknet_gpu(self, request, context):
        return request

    def pocket_sphinx(self, request, context):
        return request

    def aeneas(self, request, context):
        return request

    def object_tracking(self, request, context):
        return request

    def object_tracking_gpu(self, request, context):
        return request
