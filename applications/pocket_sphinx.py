import base64
import pocketsphinx
import pyaudio
import wave
from utils import current_milli_time
from protos import benchmark_pb2 as pb2

config = pocketsphinx.Decoder.default_config()
config.set_string('-hmm', '/usr/share/pocketsphinx/model/en-us/en-us')
config.set_string('-lm', '/usr/share/pocketsphinx/model/en-us/en-us.lm.bin')
config.set_string('-dict', '/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict')
decoder = pocketsphinx.Decoder(config)

def convert_to_text(request, request_received_time_ms):
    print("[x] Speech-to-Text Request Received")
    audio_file = 'audio_ps.wav'
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

    # pa = pyaudio.PyAudio()
    # # Open the audio file
    # wf = wave.open('audio.wav', 'rb')
    #
    # # Define a callback function for the audio stream
    # def audio_callback(in_data, frame_count, time_info, status):
    #     data = wf.readframes(frame_count)
    #     return (data, pyaudio.paContinue)
    #
    # # Open an audio stream
    # stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
    #                  channels=wf.getnchannels(),
    #                  rate=wf.getframerate(),
    #                  output=True,
    #                  stream_callback=audio_callback)
    #
    # # Start the audio stream
    # stream.start_stream()
    #
    # # Decode the audio
    # decoder.start_utt()
    # while True:
    #     # Read audio data from the stream
    #     data = stream.read(1024)
    #     if not data:
    #         break
    #     # Process the audio data
    #     decoder.process_raw(data, False, False)
    # decoder.end_utt()

    # Perform speech-to-text conversion using PocketSphinx
    with open(audio_file, 'rb') as f:
        audio = f.read()
        decoder.start_utt()
        decoder.process_raw(audio, False, True)
        decoder.end_utt()
        hypothesis = decoder.hyp()
        audio_text = hypothesis.hypstr
        print("Speech-to-Text:", audio_text)

    conversion_response = pb2.SpeechToTextResponse()
    conversion_response.text_conversion_output = audio_text
    conversion_response.request_time_ms = request_time_ms
    conversion_response.request_received_time_ms = request_received_time_ms
    conversion_response.response_time_ms = current_milli_time()

    return conversion_response
    # Get the result
    # result = decoder.hyp().hypstr
    #
    # # Print the result
    # # print(result)
    #
    # # Stop and close the audio stream and audio object
    # stream.stop_stream()
    # stream.close()
    # pa.terminate()
    # wf.close()
    #
    # conversion_response = pb2.PocketSphinxResponse()
    # conversion_response.conversion_result = result  # decoder.hyp().hypstr
    # conversion_response.request_time_ms = request.request_time_ms
    # conversion_response.request_received_time_ms = request_received_time_ms
    # conversion_response.response_time_ms = current_milli_time()
    #
    # return conversion_response