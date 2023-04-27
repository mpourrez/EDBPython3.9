from protos import benchmark_pb2_grpc as pb2_grpc

from applications.micro_benchmarks import matrix_multiplication, floating_point_sqrt, floating_point_sin, \
    fast_fourier_transform, sorter, dd_cmd, iperf3
from utils import current_milli_time

import multiprocessing


class MicroBenchmarksGRPCService(pb2_grpc.MicroBenchmarksServicer):
    def multiply_matrices(self, request, context):
        request_received_time_ms = current_milli_time()
        multiplication_response = matrix_multiplication.multiply(request, request_received_time_ms)
        return multiplication_response

    def fast_fourier_transform(self, request, context):
        request_received_time_ms = current_milli_time()
        fourier_response = fast_fourier_transform.transform(request, request_received_time_ms)
        return fourier_response

    def floating_point_sqrt(self, request, context):
        request_received_time_ms = current_milli_time()
        sqrt_response = floating_point_sqrt.sqrt(request, request_received_time_ms)
        return sqrt_response

    def floating_point_sin(self, request, context):
        request_received_time_ms = current_milli_time()
        sine_response = floating_point_sin.sine(request, request_received_time_ms)
        return sine_response

    def sort_file(self, request, context):
        request_received_time_ms = current_milli_time()
        sort_response = sorter.sort(request, request_received_time_ms)
        return sort_response

    def dd_cmd(self, request, context):
        request_received_time_ms = current_milli_time()
        dd_response = dd_cmd.dd(request, request_received_time_ms)
        return dd_response

    def run_iperf(self, request, context):
        request_received_time_ms = current_milli_time()
        iperf_response = iperf3.run_iperf(request, request_received_time_ms)
        return iperf_response