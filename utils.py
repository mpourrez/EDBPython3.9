import time
from base64 import b64decode, b64encode
import cv2
import numpy as np

import constants


def current_milli_time():
    return round(time.time() * 1000)


def extract_image(request_image):
    byte_array = bytearray(request_image, encoding='utf-8')
    decoded_bytes = b64decode(byte_array)
    numpy_array = np.frombuffer(decoded_bytes, np.uint8)
    image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
    return image


def read_input_workload_frame(frame_id):
    count_frame_id_digits = 1
    workload_input_path = constants.WORKLOAD_INPUT_PATH
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
