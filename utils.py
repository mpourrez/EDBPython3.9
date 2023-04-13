import time
from base64 import b64decode, b64encode
import cv2
import numpy as np
from io import BytesIO
from pydub import AudioSegment
import soundfile as sf
import pandas as pd
import librosa

import os
import random
import linecache

import configs


def current_milli_time():
    return round(time.time() * 1000)


random.seed(42)
random_tracking_start = random.randint(0, 429)
current_tracking_number = random_tracking_start
audio_directory = "workloads/LibriSpeech-dev-clean"  # path to audio files dataset
sentiment_filename = "workloads/stanfordSentimentTreebank/datasetSentences.txt"  # Sentiment Analysis dataset
image_dataset_directory = "workloads/coco-dataset-val2017"  # image dataset (coco)
audio_alignment_dataset_dir = "workloads/Mozilla-dataset-2022-12-07/en"

# get the path of the script and its directory
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

# Read the CSV file containing the metadata for the audio files and transcriptions
audio_alignment_metadata_file = os.path.join(script_dir, audio_alignment_dataset_dir, "validated.tsv")
audio_alignment_metadata_df = pd.read_csv(audio_alignment_metadata_file, delimiter="\t")

# count the number of lines in the file
num_lines_in_sentiment_dataset = sum(1 for line in open(os.path.join(script_dir,sentiment_filename)))

# get a list of all files in the directory
image_files = os.listdir(os.path.join(script_dir, image_dataset_directory))

# filter out any non-files (e.g. subdirectories)
image_files = [f for f in image_files if os.path.isfile(os.path.join(script_dir, image_dataset_directory, f))]

# get a list of all audio dataset files and subdirectories in the directory
all_audio_files = []
for root, dirs, files in os.walk(audio_directory):
    for file in files:
        all_audio_files.append(os.path.join(root, file))

# filter out any directories from the list of files
audio_files = [f for f in all_audio_files if os.path.isfile(f)]


def get_random_image():
    # get a random file from the list
    random_file = random.choice(image_files)
    im = cv2.imread(random_file)
    ret, buffer = cv2.imencode('.jpg', im)
    jpg_as_text = b64encode(buffer)
    base64_string = jpg_as_text.decode('utf-8')
    return base64_string


def get_random_sentiment_text():
    # choose a random line number
    random_line_num = random.randint(1, num_lines_in_sentiment_dataset)
    # get the random line
    random_line = linecache.getline(sentiment_filename, random_line_num)
    return random_line


def get_random_audio():
    # get a random file from the list
    random_file = random.choice(audio_files)
    data, sample_rate = sf.read(random_file)

    # Convert the audio data to a Base64 string
    audio_base64 = b64encode(data).decode('utf-8')
    return audio_base64


def get_random_audio_text_for_alignment():
    # Select a random row from the metadata DataFrame
    random_row = audio_alignment_metadata_df.sample(n=1).iloc[0]

    # Load the audio file and transcription for the selected row
    audio_path = os.path.join(audio_alignment_dataset_dir, "clips", random_row["path"] + ".mp3")
    transcription = random_row["sentence"]
    audio_data, sample_rate = librosa.load(audio_path)
    # Encode the audio data as a Base64 string
    audio_base64 = b64encode(audio_data).decode('utf-8')
    return audio_base64, transcription


def get_random_image_for_tracking():
    global current_tracking_number
    if current_tracking_number > 429:
        current_tracking_number = 1
    count_frame_id_digits = 1
    workload_input_path = configs.WORKLOAD_INPUT_PATH
    if current_tracking_number > 9:
        if current_tracking_number > 99:
            count_frame_id_digits = 3
        else:
            count_frame_id_digits = 2
    image_file = workload_input_path + "0" * (6 - count_frame_id_digits) + str(current_tracking_number) + '.jpg'
    im = cv2.imread(image_file)
    ret, buffer = cv2.imencode('.jpg', im)
    jpg_as_text = b64encode(buffer)
    base64_string = jpg_as_text.decode('utf-8')
    current_tracking_number += 1
    return base64_string


def get_avg_without_outlier(data_list):
    if np.std(data_list) == 0:
        return sum(data_list) / len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    for i in range(0, len(data_list)):
        if z[i] > -3 and z[i] < 3:
            avg += data_list[i]
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))
    return avg / count


def get_std_without_outlier(data_list):
    if np.std(data_list) == 0:
        return sum(data_list) / len(data_list)
    z = np.abs(stats.zscore(data_list))
    avg = 0
    count = 0
    list_without_outliers = []
    for i in range(0, len(data_list)):
        if z[i] > -3 and z[i] < 3:
            list_without_outliers.append(data_list[i])
            count += 1
        else:
            print("This is outlier: {}".format(data_list[i]))

    a = 1.0 * np.array(list_without_outliers)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + 0.95) / 2., n - 1)
    return h


####################################
# OLD CODES BELOW ##################
####################################


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
