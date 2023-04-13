from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from protos import benchmark_pb2 as pb2
from utils import current_milli_time


def align_speech_text(audio_data, text_data, request, request_received_time_ms):
    # Create audio and text objects from binary data
    audio_path = "audio.mp3"
    with open(audio_path, "wb") as f:
        f.write(audio_data)

    # save the decoded text data as a temporary file in plain text format
    text_path = "text.txt"
    with open(text_path, "wb") as f:
        f.write(text_data)

    config_string = "task_language=eng|is_text_type=plain"
    task = Task(config_string)
    task.audio_file_path_absolute = "audio.mp3"
    task.text_file_path_absolute = "text.txt"

    ExecuteTask(task).execute()

    result = ""
    for frag in task.sync_map.fragments:
        result += str(frag)

    alignment_result = pb2.AudioTextResponse()
    alignment_result.alignment_result = result
    alignment_result.request_time_ms = request.request_time_ms
    alignment_result.request_received_time_ms = request_received_time_ms
    alignment_result.response_time_ms = current_milli_time()
    print("[x] Speech-to-Text - Responded the client request")
    return alignment_result
