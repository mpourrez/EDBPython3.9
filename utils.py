import time
from base64 import b64decode, b64encode
import cv2
import numpy as np
from io import BytesIO
from pydub import AudioSegment

import configs


def current_milli_time():
    return round(time.time() * 1000)


def bytes_to_mb(bytes):
    KB = 1024  # One Kilobyte is 1024 bytes
    MB = KB * 1024  # One MB is 1024 KB
    return int(bytes / MB)


def extract_image(request_image):
    byte_array = bytearray(request_image, encoding='utf-8')
    decoded_bytes = b64decode(byte_array)
    numpy_array = np.frombuffer(decoded_bytes, np.uint8)
    image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
    return image


def read_input_workload_frame(frame_id):
    count_frame_id_digits = 1
    workload_input_path = configs.WORKLOAD_INPUT_PATH
    if frame_id > 9:
        if frame_id > 99:
            count_frame_id_digits = 3
        else:
            count_frame_id_digits = 2

    image_file = workload_input_path + "0" * (6 - count_frame_id_digits) + str(frame_id) + '.jpg'
    print('Frame:', image_file)
    im = cv2.imread(image_file)
    ret, buffer = cv2.imencode('.jpg', im)
    jpg_as_text = b64encode(buffer)
    base64_string = jpg_as_text.decode('utf-8')
    return base64_string


def extract_audio(request_audio):
    byte_array = bytearray(request_audio, encoding='utf-8')
    decoded_bytes = b64decode(byte_array)
    return decoded_bytes


def read_audio_workload():
    with open('workloads/audio/DeFog_b0430.wav', 'rb') as audio_file:
        audio_data = audio_file.read()
        base64_data = b64encode(audio_data).decode('utf-8')
    return base64_data


def read_aeneas_audio_workload():
    audio = AudioSegment.from_file("workloads/aeneas/DeFog_p001.mp3", format="mp3")
    first_five_seconds = audio[:5000]
    audio_bytes = BytesIO()
    first_five_seconds.export(audio_bytes, format("mp3"))
    audio_base64 = b64encode(audio_bytes.getvalue()).decode("utf-8")
    # with open('workloads/aeneas/DeFog_p001.mp3', 'rb') as audio_file:
    #     audio_data = audio_file.read()
    #     base64_data = b64encode(audio_data).decode('utf-8')
    return audio_base64


def read_aeneas_text_workload():
    with open('workloads/aeneas/p001.xhtml', 'rb') as text_file:
        text_date = text_file.read()
        base64_data = b64encode(text_date).decode('utf-8')
    return base64_data
