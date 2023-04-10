import base64
import pocketsphinx
import pyaudio
from utils import current_milli_time
from protos import benchmark_pb2 as pb2


def convert_to_text(request, request_received_time_ms):
    # decode the base64 string to bytes
    audio_data = base64.b64decode(request.audio)

    # write the bytes data to a WAV file
    with open('audio.wav', 'wb') as f:
        f.write(audio_data)

    # create a Pocketsphinx decoder
    config = pocketsphinx.Decoder.default_config()
    config.set_string('-hmm', '/pocket_sphinx/cmusphinx-en-us-8khz-5.2')
    config.set_string('-lm', '/pocket_sphinx/en-70k-0.2-pruned.lm.gz')
    config.set_string('-dict', '/pocket_sphinx/cmudict.dict')
    decoder = pocketsphinx.Decoder(config)

    # open the audio file and read in the data
    p = pyaudio.PyAudio()
    with open('audio.wav', 'rb') as f:
        audio_data = f.read()

    # start the audio stream
    stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)
    stream.start_stream()

    # decode the audio
    decoder.start_utt()
    decoder.process_raw(audio_data, False, True)
    decoder.end_utt()

    conversion_response = pb2.PocketSphinxResponse()
    conversion_response.conversion_result = decoder.hyp().hypstr
    conversion_response.request_time_ms = request.request_time_ms
    conversion_response.request_received_time_ms = request_received_time_ms
    conversion_response.response_time_ms = current_milli_time()

    return conversion_response
