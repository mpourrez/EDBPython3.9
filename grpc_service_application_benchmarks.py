from applications.object_tracking import object_tracker
from applications.object_detection import object_detector
from applications.pocket_sphinx import pocketsphinx
from applications.aeneas import speech_text_aligner
from applications import sentiment_analysis, image_processing, speech_to_text, image_classification_alexnet_cpu,\
    image_classification_alexnet_gpu, image_classification_squeezenet_cpu, image_classification_squeezenet_gpu,\
    object_detection_darknet_cpu, object_detection_darknet_gpu, pocket_sphinx, aeneas, \
    object_tracking_gpu, object_tracking_cpu
from utils import *
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
        request_received_time_ms = current_milli_time()
        conversion_result = speech_to_text.convert_to_text(request, request_received_time_ms)
        return conversion_result

    def image_classification_alexnet(self, request, context):
        request_received_time_ms = current_milli_time()
        classification_result = image_classification_alexnet_cpu.classify(request, request_received_time_ms)
        return classification_result

    def image_classification_alexnet_gpu(self, request, context):
        request_received_time_ms = current_milli_time()
        classification_result = image_classification_alexnet_gpu.classify(request, request_received_time_ms)
        return classification_result

    def image_classification_squeezenet(self, request, context):
        request_received_time_ms = current_milli_time()
        classification_result = image_classification_squeezenet_cpu.classify(request, request_received_time_ms)
        return classification_result

    def image_classification_squeezenet_gpu(self, request, context):
        request_received_time_ms = current_milli_time()
        classification_result = image_classification_squeezenet_gpu.classify(request, request_received_time_ms)
        return classification_result

    def object_detection_darknet(self, request, context):
        request_received_time_ms = current_milli_time()
        detection_result = object_detection_darknet_cpu.detect(request, request_received_time_ms)
        return detection_result

    def object_detection_darknet_gpu(self, request, context):
        request_received_time_ms = current_milli_time()
        detection_result = object_detection_darknet_gpu.detect(request, request_received_time_ms)
        return detection_result

    def pocket_sphinx(self, request, context):
        request_received_time_ms = current_milli_time()
        conversion_result = pocket_sphinx.convert_to_text(request, request_received_time_ms)
        return conversion_result

    def aeneas(self, request, context):
        request_received_time_ms = current_milli_time()
        audio_data = extract_audio(request.audio)
        text_data = extract_audio(request.text_input)
        speech_to_text_result = aeneas.align_speech_text(audio_data, text_data, request, request_received_time_ms)
        return speech_to_text_result

    def object_tracking(self, request, context):
        request_received_time_ms = current_milli_time()
        tracking_result = object_tracking_cpu.track(request, request_received_time_ms)
        return tracking_result

    def object_tracking_gpu(self, request, context):
        request_received_time_ms = current_milli_time()
        tracking_result = object_tracking_gpu.track(request, request_received_time_ms)
        return tracking_result

    ######################################################
    ######################################################
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

    def pocketsphinx(self, request, context):
        request_received_time_ms = current_milli_time()
        audio = extract_audio(request.image)
        speech_to_text_result = pocketsphinx.convert_to_text(audio, request.frame_id, request.request_time_ms,
                                                             request_received_time_ms)
        return speech_to_text_result

    def align_speech_text(self, request, context):
        request_received_time_ms = current_milli_time()
        audio_data = extract_audio(request.audio)
        text_data = extract_audio(request.text_input)
        speech_to_text_result = speech_text_aligner.align_speech_text(audio_data, text_data, request.frame_id,
                                                                      request.request_time_ms,
                                                                      request_received_time_ms)
        return speech_to_text_result

