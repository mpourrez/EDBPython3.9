import grpc
from concurrent import futures
import psutil
import tracemalloc
import subprocess

from protos import benchmark_pb2_grpc as pb2_grpc
from utils import *
from applications.object_tracking import object_tracker
from applications.object_detection import object_detector
from protos import benchmark_pb2 as pb2


class BenchmarkService(pb2_grpc.BenchmarksServicer):

    def __init__(self, *args, **kwargs):
        self.fault_injection_process = None

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

    def get_cpu_trace(self, request, context):
        # This method gives the cpu load over the last 1 minute, 5 minutes, and 15 minutes
        # Since our experiments duration is 1 minute --> we can use the first one
        load1, load5, load15 = psutil.getloadavg()
        cpu_trace = pb2.CPUTrace()
        cpu_trace.cpu_load = (load1 / psutil.cpu_count()) * 100
        return cpu_trace

    def get_memory_usage(self, request, context):
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_trace = pb2.MemoryTrace()
        memory_trace.current_memory_mb = current / 10 ** 6
        memory_trace.peak_memory_mb = peak / 10 ** 6
        return memory_trace

    def start_memory_tracing(self, request, context):
        tracemalloc.start()
        return pb2.EmptyProto()

    def inject_fault(self, request, context):
        fault_command = request.fault_command
        fault_config = request.fault_config
        # I'll make the stressor to run for a bit longer than experiment-time to make sure experiment is done
        timeout = request.timeout + configs.TIME_BOUND_FOR_FAULT_INJECTION
        stress_string = 'stress-ng {0} {1} --timeout {2}s'
        shell_command = stress_string.format(fault_command, fault_config, str(timeout))
        print("[x] Stress command to run: " + shell_command)
        self.fault_injection_process = subprocess.Popen(shell_command, shell=True)
        return pb2.EmptyProto()

    def get_fault_injection_status(self, request, context):
        if self.fault_injection_process is None:
            # No faults has been injected yet
            return pb2.FaultInjectionStatus(is_finished=True)
        poll = self.fault_injection_process.poll()
        if poll is None:
            # A None value indicates that the process hasn't terminated yet
            print("[xxxx] Fault Injection Still in Process")
            return pb2.FaultInjectionStatus(is_finished=False)
        else:
            return pb2.FaultInjectionStatus(is_finished=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_BenchmarksServicer_to_server(BenchmarkService(), server)
    server.add_insecure_port('[::]:50051')
    print("Listening on Port 50051 ...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
