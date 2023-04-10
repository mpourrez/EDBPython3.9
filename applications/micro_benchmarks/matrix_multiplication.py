import numpy as np

from protos import benchmark_pb2 as pb2
from utils import current_milli_time


def multiply(request, request_received_time_ms):
    matrix_1 = deserialize_matrix(request.matrix_1)
    matrix_2 = deserialize_matrix(request.matrix_2)

    for i in range(300):
        multiplied_matrix = np.matmul(matrix_1, matrix_2)
    rows = []
    for i in range(multiplied_matrix.shape[0]):
        row = pb2.Row(values=list(multiplied_matrix[i]))
        rows.append(row)
    serialized_matrix = pb2.Matrix(rows=rows)

    multiplication_response = pb2.MatrixMultiplicationResponse(matrix=serialized_matrix)
    multiplication_response.request_time_ms = request.request_time_ms
    multiplication_response.request_received_time_ms = request_received_time_ms
    multiplication_response.response_time_ms = current_milli_time()

    return multiplication_response


def deserialize_matrix(request_matrix):
    # Deserialize the matrix from the request
    matrix = np.zeros((len(request_matrix.rows), len(request_matrix.rows[0].values)))
    for i, row in enumerate(request_matrix.rows):
        matrix[i, :] = row.values
    return matrix
