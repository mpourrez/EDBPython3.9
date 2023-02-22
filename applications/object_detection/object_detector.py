import time
from absl import app, logging
import cv2
import numpy as np
import tensorflow as tf
from applications.object_detection.yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from applications.object_detection.yolov3_tf2.dataset import transform_images, load_tfrecord_dataset
from protos import benchmark_pb2 as pb2
from utils import current_milli_time

# customize your API through the following parameters
classes_path = './applications/object_detection/data/labels/coco.names'
weights_path = './applications/object_detection/weights/yolov3-tiny.tf'
tiny = True                    # set to True if using a Yolov3 Tiny model
size = 416                      # size images are resized to for model
# output_path = './applications/object_detection/detections/'   # path to output folder where images with detections are saved
num_classes = 80                # number of classes in model

# load in weights and classes
physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

if tiny:
    yolo = YoloV3Tiny(classes=num_classes)
else:
    yolo = YoloV3(classes=num_classes)

yolo.load_weights(weights_path).expect_partial()
print('weights loaded')

class_names = [c.strip() for c in open(classes_path).readlines()]
print('classes loaded')

def detect_objects(image, frame_id, request_time, request_received_time):

    # create list of responses for current image
    raw_img = image
    img = tf.expand_dims(raw_img, 0)
    img = transform_images(img, size)

    t1 = time.time()
    boxes, scores, classes, nums = yolo(img)
    t2 = time.time()
    print('time: {}'.format(t2 - t1))

    print('detections:')
    detected_objects = []
    for i in range(nums[0]):
        print('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
                                        np.array(scores[0][i]),
                                        np.array(boxes[0][i])))
        bbox = np.array(boxes[0][i])
        tracked_object = pb2.DetectedTrackedObject()
        tracked_object.clazz = class_names[int(classes[0][i])]
        # The bounding box need to be scaled based on the size of image
        # TODO: get the size of image and scale the bounding box
        tracked_object.x_min = int(bbox[0]* 416)
        tracked_object.y_min = int(bbox[1]* 712)
        tracked_object.x_max = int(bbox[2]* 416)
        tracked_object.y_max = int(bbox[3]* 712)
        detected_objects.append(tracked_object)

    tracking_result = pb2.DetectionTrackingResponse()
    tracking_result.frame_id = frame_id
    tracking_result.request_time_ms = request_time
    tracking_result.request_received_time_ms = request_received_time
    tracking_result.response_time_ms = current_milli_time()
    tracking_result.detected_objects.extend(detected_objects)
    return tracking_result


