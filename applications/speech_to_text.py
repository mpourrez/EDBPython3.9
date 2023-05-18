import speech_recognition as sr
from utils import current_milli_time
from protos import benchmark_pb2 as pb2

def convert_to_text(request, request_received_time_ms):
    print("[x] Speech-to-Text Request Received")
    audio_file = 'audio_st.wav'
    first_chunk = True
    audio_data = bytearray()
    for audio_chunk in request:
        if first_chunk:
            first_chunk = False
            request_time_ms = audio_chunk.request_time_ms
        audio_data.extend(audio_chunk.audio)
    # Save the audio chunk to a file
    with open(audio_file, "wb") as f:
        f.write(audio_data)

    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
        audio_text = r.recognize_google(audio)
        print("Speech-to-Text:", audio_text)
    conversion_response = pb2.SpeechToTextResponse()
    conversion_response.text_conversion_output = audio_text
    conversion_response.request_time_ms = request_time_ms
    conversion_response.request_received_time_ms = request_received_time_ms
    conversion_response.response_time_ms = current_milli_time()

    return conversion_response

