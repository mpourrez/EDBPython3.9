from utils import current_milli_time
from protos import benchmark_pb2 as pb2
import numpy as np
import cv2
import base64
import darknetpy

# load the configuration file and weights
cfg_file = 'yolo_configurations/yolov3-tiny.cfg'
weights_file = 'yolo_configurations/yolov3-tiny.weights'
net = darknetpy.load_net_custom(cfg_file.encode('utf-8'), weights_file.encode('utf-8'), 0, 1)
meta = darknetpy.load_meta('yolo_configurations/my_model.data'.encode('utf-8'))


def detect(request, request_received_time_ms):
    # decode the base64string to bytes
    image_data = base64.b64decode(request.image)

    # convert bytes data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)

    # decode numpy array to OpenCV image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # resize the image to the network input size
    width = darknetpy.network_width(net)
    height = darknetpy.network_height(net)
    resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    # convert image to darknet format
    darknet_image = darknetpy.make_image(width, height, 3)
    darknetpy.copy_image_from_bytes(darknet_image, resized.tobytes())

    # detect objects in the image
    detections = darknetpy.detect_image(net, meta, darknet_image, thresh=0.5, hier_thresh=0.5, nms=0.45, debug=False,
                                        use_cuda=True)

    detected_objects = []
    for detection in detections:
        class_name = detection[0].decode('utf-8')
        x, y, w, h = detection[2]

        detected_objects = pb2.DetectedTrackedObject()
        detected_objects.clazz = class_name
        detected_objects.x_min = x
        detected_objects.y_min = y
        detected_objects.x_max = w
        detected_objects.y_max = h
        detected_objects.append(detected_objects)

    detection_result = pb2.ObjectDetectionResponse()
    detection_result.request_time_ms = request.request_time_ms
    detection_result.request_received_time_ms = request_received_time_ms
    detection_result.response_time_ms = current_milli_time()
    detection_result.detected_objects.extend(detected_objects)
    print("[x] Object-detection - Responded the client request")
    return detection_result
