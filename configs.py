#!/usr/bin/env python
# encoding: utf-8
"""
configs.py
"""

MAX_FRAME_NUM = 250
FPS = 5
WORKLOAD_INPUT_PATH = './workloads/MOT20-01/img1/'
MAX_EXPERIMENT_TIME_SECONDS = 100 #in-seconds - make it more than the time of video (for 1-min video set 100 seconds)
TIME_BOUND_FOR_FAULT_INJECTION = 10 #in-seconds
REPEAT_EXPERIMENTS = 10

EDGE_DEVICE_NAME = 'raspberrypi'
EDGE_DEVICE_IP = '192.168.0.168'
EDGE_DEVICE_PORT = 50051

APPLICATIONS = ['object_detection', 'object_tracking']

class Fault:
    def __init__(self, fault_name, abbreviation, fault_command, fault_config):
        self.fault_name = fault_name
        self.abbreviation = abbreviation
        self.fault_command = fault_command
        self.fault_config = fault_config


FAULTS = [
    Fault('cpu-overload', 'CPU', '--cpu 0 --cpu-load', ['20', '40', '60', '80']),
    Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['20%', '40%', '60%', '80%']),
    Fault('hdd-overload', 'HDD', '--hdd 0 --hdd-bytes', ['20%', '40%', '60%', '80%']),
    Fault('io-stress', 'IO', '--io', ['100']),
    Fault('cache-thrashing', 'CCHE', '--cache', ['0']),
    Fault('page-fault', 'PF', '--fault', ['0']),
    Fault('interrupts', 'INTR', '--sleep ', ['32']),
    Fault('ping-flood', 'PING', 'ping', ['-i 0.3', '-i 0.2', '-i 0.1', '-f'])
]

