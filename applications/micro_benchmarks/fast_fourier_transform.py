import numpy as np

from protos import benchmark_pb2 as pb2
from utils import current_milli_time


def transform(request, request_received_time_ms):
    fourier_input = request.input_sequence.values
    for i in range(50):
        fourier_result = np.fft.fft(fourier_input)

    fourier_response = pb2.FastFourierResponse(fourier_output=pb2.Row(values=list(fourier_result)))
    fourier_response.request_time_ms = request.request_time_ms
    fourier_response.request_received_time_ms = request_received_time_ms
    fourier_response.response_time_ms = current_milli_time()

    return fourier_response
