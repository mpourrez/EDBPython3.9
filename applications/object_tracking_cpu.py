import cv2
import numpy as np
from base64 import b64decode
from yolov4.tf import YOLOv4
from deep_sort import deepsort_tracker

from utils import current_milli_time
from protos import benchmark_pb2 as pb2

# Load YOLOv4 model
yolo = YOLOv4()

# Load DeepSORT model
deepsort = deepsort_tracker.DeepSortTracker()


def track(request, request_received_time_ms):
    # Decode base64 frame
    frame = np.frombuffer(b64decode(request.image), np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # Detect objects
    detections = yolo.detect_objects(frame)

    # Perform tracking
    tracked_objects = deepsort.run_deep_sort(frame, detections)

    objects = []
    # Visualize results
    for obj in tracked_objects:
        bbox = obj['bbox']
        cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)
        cv2.putText(frame, f"{obj['id']}", (int(bbox[0]), int(bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (0, 0, 255), 2)

        objects = pb2.DetectedTrackedObject()
        objects.x_min = int(bbox[0])
        objects.y_min = int(bbox[1])
        objects.x_max = int(bbox[2])
        objects.y_max = int(bbox[3])
        objects.append(objects)

    tracking_result = pb2.ObjectTrackingRequest()
    tracking_result.request_time_ms = request.request_time_ms
    tracking_result.request_received_time_ms = request_received_time_ms
    tracking_result.response_time_ms = current_milli_time()
    tracking_result.tracked_objects.extend(objects)
    print("[x] Object-tracking - Responded the client request")
    return tracking_result
