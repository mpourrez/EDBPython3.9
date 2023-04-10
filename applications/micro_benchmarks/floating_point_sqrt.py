import math

from protos import benchmark_pb2 as pb2
from utils import current_milli_time


def sqrt(request, request_received_time_ms):
    """This function will calculate sqrt multiple times"""
    for i in range(40000001):
        result = math.sqrt(request.floating_point_input)
    floating_point_response = pb2.FloatingPointResponse()
    floating_point_response.floating_point_output = result
    floating_point_response.request_time_ms = request.request_time_ms
    floating_point_response.request_received_time_ms = request_received_time_ms
    floating_point_response.response_time_ms = current_milli_time()
    return floating_point_response
