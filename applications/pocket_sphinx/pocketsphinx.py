import base64
import io
import os
import pocketsphinx
import speech_recognition as sr

from protos import benchmark_pb2 as pb2
from utils import current_milli_time

def convert_to_text(audio, frame_id, request_time_ms, request_received_time_ms):
    # Decode the base64 audio bytes to a raw audio bytes object
    audio_stream = io.BytesIO(audio)

    # Set up the SpeechRecognition AudioFile object with the BytesIO object
    with sr.AudioFile(audio_stream) as source:
        # Initialize the recognizer and perform speech recognition
        recognizer = sr.Recognizer()
        audio = recognizer.record(source)
        text = recognizer.recognize_sphinx(audio)

        tracking_result = pb2.PocketSphinxResponse()
        tracking_result.frame_id = frame_id
        tracking_result.request_time_ms = request_time_ms
        tracking_result.request_received_time_ms = request_received_time_ms
        tracking_result.response_time_ms = current_milli_time()
        tracking_result.conversion_result = text
        print("[x] Speech-to-Text - Responded the client request")
        return tracking_result
