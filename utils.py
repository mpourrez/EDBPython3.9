import time
from base64 import b64decode
import cv2
import numpy as np


def current_milli_time():
    return round(time.time() * 1000)


def extract_image(request_image):
    byte_array = bytearray(request_image, encoding='utf-8')
    decoded_bytes = b64decode(byte_array)
    numpy_array = np.frombuffer(decoded_bytes, np.uint8)
    image = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
    return image
