from protos import benchmark_pb2_grpc as pb2_grpc

from applications.micro_benchmarks import fast_fourier_transform
from utils import current_milli_time


class MicroBenchmarksGRPCService(pb2_grpc.MicroBenchmarksServicer):

    def fast_fourier_transform(self, request, context):
        request_received_time_ms = current_milli_time()
        fourier_response = fast_fourier_transform.transform(request, request_received_time_ms)
        return fourier_response

