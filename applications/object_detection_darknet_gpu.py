import base64
import subprocess
import torch
import torchvision.transforms as transforms
from PIL import Image
from utils import current_milli_time
from protos import benchmark_pb2 as pb2

# # Check if a GPU is available and set the device accordingly
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("[x] Device found: {0}".format(device))

def detect(request, request_received_time_ms):
    # Decode base64 string to binary format
    binary_data = base64.b64decode(request.image)

    # Save binary data to a file
    with open('input.jpg', 'wb') as f:
        f.write(binary_data)

    # Load the image and apply transformations
    image = Image.open('input.jpg').convert('RGB')
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0).to(device)

    # Use Darknet to perform object detection
    cmd = ['darknet', 'detect', 'cfg/yolov3.cfg', 'yolov3.weights', 'input.jpg']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()

    # Parse the output of Darknet and return the results
    results = []
    detected_objects = []
    lines = output.decode().split('\n')
    for line in lines:
        if line.startswith('Enter Image Path:'):
            continue
        if not line.strip():
            continue
        if '%' in line:
            continue
        if ':' in line:
            parts = line.split(':')
            label = parts[0].strip()
            confidence = float(parts[1].strip().replace('%', '')) / 100.0
            results.append((label, confidence))
            detected_object = pb2.DetectedTrackedObject()
            detected_object.clazz = label
            detected_objects.append(detected_object)

    detection_result = pb2.ObjectDetectionResponse()
    detection_result.request_time_ms = request.request_time_ms
    detection_result.request_received_time_ms = request_received_time_ms
    detection_result.response_time_ms = current_milli_time()
    detection_result.detected_objects.extend(detected_objects)
    print("[x] Object-detection - Responded to the client request")
    return detection_result