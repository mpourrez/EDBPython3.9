import os
import time
import tensorflow as tf
from absl import app, flags, logging
from absl.flags import FLAGS
import applications.object_tracking.core.utils as utils
from applications.object_tracking.core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from applications.object_tracking.core.config import cfg
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
# deep sort imports
from applications.object_tracking.deep_sort import preprocessing, nn_matching
from applications.object_tracking.deep_sort.detection import Detection
from applications.object_tracking.deep_sort.tracker import Tracker
from applications.object_tracking.tools import generate_detections as gdet

from protos import benchmark_pb2 as pb2
from utils import current_milli_time

# comment out below line to enable tensorflow logging outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

# Definition of the parameters
max_cosine_distance = 0.4
nn_budget = None
nms_max_overlap = 1.0

# initialize deep sort
model_filename = 'applications/object_tracking/model_data/mars-small128.pb'
encoder = gdet.create_box_encoder(model_filename, batch_size=1)
# calculate cosine distance metric
metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
# initialize tracker
tracker = Tracker(metric)

# load configuration for object detector
config = ConfigProto()
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config2(FLAGS)
input_size = 416  # FLAGS.size
weights = "./applications/object_tracking/checkpoints/yolov4-tiny-416"
saved_model_loaded = tf.saved_model.load(weights, tags=[tag_constants.SERVING])
infer = saved_model_loaded.signatures['serving_default']


####################################################################################
# Object Tracking and Detection using Yolov4
####################################################################################
def track_from_image(image, frame_id, request_time, request_received_time):
    print('[x] Frame #: ', frame_id)
    start_time = time.time()
    image_data = cv2.resize(image, (input_size, input_size))
    image_data = image_data / 255.
    image_data = image_data[np.newaxis, ...].astype(np.float32)

    print("before running detections")
    batch_data = tf.constant(image_data)
    pred_bbox = infer(batch_data)
    for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]

    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=50,
        max_total_size=50,
        iou_threshold=0.45,  # FLAGS.iou,
        score_threshold=0.5  # FLAGS.score
    )

    # convert data to numpy arrays and slice out unused elements
    num_objects = valid_detections.numpy()[0]
    bboxes = boxes.numpy()[0]
    bboxes = bboxes[0:int(num_objects)]
    scores = scores.numpy()[0]
    scores = scores[0:int(num_objects)]
    classes = classes.numpy()[0]
    classes = classes[0:int(num_objects)]

    # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, width, height
    original_h, original_w, _ = image.shape
    bboxes = utils.format_boxes(bboxes, original_h, original_w)

    # store all predictions in one parameter for simplicity when calling functions
    pred_bbox = [bboxes, scores, classes, num_objects]

    # read in all class names from config
    class_names = utils.read_class_names(cfg.YOLO.CLASSES)

    # by default allow all classes in .names file
    allowed_classes = list(class_names.values())

    # loop through objects and use class index to get class name, allow only classes in allowed_classes list
    names = []
    deleted_indx = []
    for i in range(num_objects):
        class_indx = int(classes[i])
        class_name = class_names[class_indx]
        if class_name not in allowed_classes:
            deleted_indx.append(i)
        else:
            names.append(class_name)
    names = np.array(names)
    count = len(names)
    bboxes = np.delete(bboxes, deleted_indx, axis=0)
    scores = np.delete(scores, deleted_indx, axis=0)

    # encode yolo detections and feed to tracker
    features = encoder(image, bboxes)
    detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in
                  zip(bboxes, scores, names, features)]
    print(detections)

    # initialize color map
    cmap = plt.get_cmap('tab20b')
    colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

    # run non-maxima supression
    boxs = np.array([d.tlwh for d in detections])
    scores = np.array([d.confidence for d in detections])
    classes = np.array([d.class_name for d in detections])
    indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
    detections = [detections[i] for i in indices]

    # Call the tracker
    tracker.predict()
    tracker.update(detections)

    # update tracks
    tracked_objects = []
    for track in tracker.tracks:
        bbox = track.to_tlbr()
        class_name = track.get_class()

        # draw bbox on screen
        color = colors[int(track.track_id) % len(colors)]
        color = [i * 255 for i in color]
        cv2.rectangle(image, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
        cv2.rectangle(image, (int(bbox[0]), int(bbox[1] - 30)),
                      (int(bbox[0]) + (len(class_name) + len(str(track.track_id))) * 17, int(bbox[1])), color, -1)
        cv2.putText(image, class_name + "-" + str(track.track_id), (int(bbox[0]), int(bbox[1] - 10)), 0, 0.75,
                    (255, 255, 255), 2)

        tracked_object = pb2.DetectedTrackedObject()
        tracked_object.track_id = track.track_id
        tracked_object.clazz = class_name
        tracked_object.x_min = int(bbox[0])
        tracked_object.y_min = int(bbox[1])
        tracked_object.x_max = int(bbox[2])
        tracked_object.y_max = int(bbox[3])

        tracked_objects.append(tracked_object)
        print("Tracker ID: {}, Class: {},  BBox Coords (xmin, ymin, xmax, ymax): {}".format(str(track.track_id),
                                                                                            class_name, (
                                                                                                int(bbox[0]),
                                                                                                int(bbox[1]),
                                                                                                int(bbox[2]),
                                                                                                int(bbox[3]))))
    # calculate frames per second of running detections
    fps = 1.0 / (time.time() - start_time)
    print("FPS: %.2f" % fps)
    tracking_result = pb2.DetectionTrackingResponse()
    tracking_result.frame_id = frame_id
    tracking_result.request_time_ms = request_time
    tracking_result.request_received_time_ms = request_received_time
    tracking_result.response_time_ms = current_milli_time()
    tracking_result.detected_objects.extend(tracked_objects)
    return tracking_result

    # session.close()
    # cv2.destroyAllWindows()
