from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from protos import benchmark_pb2 as pb2
from utils import current_milli_time

def align_speech_text(request):
    print("[x] Aeneas Request Received")
    audio_file = 'audio_ae.wav'
    transcript_file = 'transcript.txt'
    first_chunk = True
    audio_data = bytearray()
    for audio_chunk in request:
        if first_chunk:
            first_chunk = False
            request_time_ms = audio_chunk.request_time_ms
            transcript = audio_chunk.text_input
        audio_data.extend(audio_chunk.audio)
    # This is when finally all chunks are received and we are ready to process
    request_received_time_ms = current_milli_time()
    # Save the audio chunk to a file
    with open(audio_file, "wb") as f:
        f.write(audio_data)

    with open(transcript_file, "w") as f:
        f.write(transcript)

    config_string = "task_language=eng|is_text_type=plain"
    task = Task(config_string)
    task.audio_file_path_absolute = audio_file
    task.text_file_path_absolute = transcript_file
    ExecuteTask(task).execute()

    result = ""
    for frag in task.sync_map.fragments:
        result += str(frag)

    alignment_result = pb2.AudioTextResponse()
    alignment_result.alignment_result = result
    alignment_result.request_time_ms = request_time_ms
    alignment_result.request_received_time_ms = request_received_time_ms
    alignment_result.response_time_ms = current_milli_time()
    print("[x] Aeneas - Responded the client request")
    return alignment_result

