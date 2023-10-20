from utils import *
from applications import image_processing, sentiment_analysis, aeneas, pocket_sphinx, object_detection_darknet_cpu
from protos import benchmark_pb2_grpc as pb2_grpc

class ApplicationBenchmarksGRPCService(pb2_grpc.ApplicationBenchmarksServicer):

    def __init__(self, *args, **kwargs):
        self.fault_injection_process = None
        self.utilization_output = None
        self.resource_tracing_process = None

    def image_processing(self, request, context):
        request_received_time_ms = current_milli_time()
        processing_result = image_processing.resize_image(request, request_received_time_ms)
        return processing_result

    def sentiment_analysis(self, request, context):
        request_received_time_ms = current_milli_time()
        analysis_result = sentiment_analysis.analyze_sentiment(request, request_received_time_ms)
        return analysis_result

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
        request_received_time_ms = current_milli_time()
        detection_result = object_detection_darknet_cpu.detect(request, request_received_time_ms)
        return detection_result

    def object_detection_darknet_gpu(self, request, context):
        return request

    def pocket_sphinx(self, request, context):
        conversion_result = pocket_sphinx.convert_to_text(request)
        return conversion_result

    def aeneas(self, request, context):
        speech_to_text_result = aeneas.align_speech_text(request)
        return speech_to_text_result

    def object_tracking(self, request, context):
        return request

    def object_tracking_gpu(self, request, context):
        return request
