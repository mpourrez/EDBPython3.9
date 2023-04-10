import speech_recognition as sr
import io
from utils import current_milli_time, extract_audio
from protos import benchmark_pb2 as pb2


def convert_to_text(request, request_received_time_ms):
    audio = extract_audio(request.audio)
    # Decode the base64 audio bytes to a raw audio bytes object
    audio_stream = io.BytesIO(audio)

    text_conversion = ''
    recognizer = sr.Recognizer()
    # Set up the SpeechRecognition AudioFile object with the BytesIO object
    with sr.AudioFile(audio_stream) as source:
        # listen for data (load audio in memory)
        audio_data = recognizer.listen(source)
        # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        text_conversion = recognizer.recognize_google(audio_data)

    conversion_response = pb2.SpeechToTextResponse()
    conversion_response.text_conversion_output = text_conversion
    conversion_response.request_time_ms = request.request_time_ms
    conversion_response.request_received_time_ms = request_received_time_ms
    conversion_response.response_time_ms = current_milli_time()

    return conversion_response
