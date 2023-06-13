import pocketsphinx
from utils import current_milli_time
from protos import benchmark_pb2 as pb2

# config = pocketsphinx.Decoder.default_config()
# config.set_string('-hmm', '/usr/share/pocketsphinx/model/en-us/en-us')
# config.set_string('-lm', '/usr/share/pocketsphinx/model/en-us/en-us.lm.bin')
# config.set_string('-dict', '/usr/share/pocketsphinx/model/en-us/cmudict-en-us.dict')
# decoder = pocketsphinx.Decoder(config)


def convert_to_text(request):
    print("[x] Pocketsphinx Request Received")
    audio_file = 'audio_ps.wav'
    first_chunk = True
    audio_data = bytearray()
    for audio_chunk in request:
        if first_chunk:
            first_chunk = False
            request_time_ms = audio_chunk.request_time_ms
        audio_data.extend(audio_chunk.audio)
    # This is when finally all chunks are received and we are ready to process
    request_received_time_ms = current_milli_time()
    # Save the audio chunk to a file
    with open(audio_file, "wb") as f:
        f.write(audio_data)

    # Perform speech-to-text conversion using PocketSphinx
    decoder.start_utt()
    with open(audio_file, 'rb') as f:
        audio = f.read()
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
