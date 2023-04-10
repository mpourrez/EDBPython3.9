import subprocess
from protos import benchmark_pb2 as pb2
from utils import current_milli_time


def sort(request, request_received_time_ms):
    with open("received_file.txt", "wb") as f:
        f.write(request.file.data)
    command = "cat received_file.txt | sort"
    subprocess.Popen(command, shell=True)

    with open("received_file.txt", "rb") as f:
        data = f.read()

    file_data = pb2.FileData()
    file_data.data = data

    sorter_response = pb2.FileSorterResponse(sorted_file=file_data)
    sorter_response.request_time_ms = request.request_time_ms
    sorter_response.request_received_time_ms = request_received_time_ms
    sorter_response.response_time_ms = current_milli_time()

    return sorter_response
