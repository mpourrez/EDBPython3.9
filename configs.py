#!/usr/bin/env python
# encoding: utf-8
"""
configs.py
"""

MAX_FRAME_NUM = 300
WORKLOAD_INPUT_PATH = './workloads/MOT20-01/img1/'
MAX_EXPERIMENT_TIME_SECONDS = 60
TIME_BOUND_FOR_FAULT_INJECTION = 5 #in-seconds
REPEAT_EXPERIMENTS = 10

EDGE_DEVICE_NAME = 'raspberrypi'
EDGE_DEVICE_IP = '192.168.0.20'
EDGE_DEVICE_PORT = 50051

APPLICATIONS = ['object_detection', 'object_tracking','pocketsphinx']

class Fault:
    def __init__(self, fault_name, abbreviation, fault_command, fault_config):
        self.fault_name = fault_name
        self.abbreviation = abbreviation
        self.fault_command = fault_command
        self.fault_config = fault_config

FAULTS = [
    #Fault('page-fault', 'PF', '--fault', ['0']),
    Fault('io-stress', 'IO', '--io', ['100']),
    #Fault('hdd-overload', 'HDD', '--hdd 0 --hdd-bytes', ['60%']),
    #Fault('cpu-overload', 'CPU', '--cpu 0 --cpu-load', ['20', '50', '80']),
    Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['60%']),
    #Fault('cache-thrashing', 'CCHE', '--cache', ['0']),
    #Fault('contextswitch', 'CTXS', '--cswitch --cswitch-ops', ['10000']),
    # Fault('ping-flood', 'PING', '', ['faster']),
    # Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['20%', '60%', '90%']),
    # Fault('cpu-overload', 'CPU2', '--cpu 0 --cpu-load', ['20', '50', '80']),
    # Fault('hdd-overload', 'HDD', '--hdd 0 --hdd-bytes', [ '20%']),
    # Fault('hdd-overload', 'HDD2', '--hdd 0 --hdd-bytes', [ '60%']),
    # Fault('hdd-overload', 'HDD', '--hdd 0 --hdd-bytes', [ '90%']),
    #Fault('ping-flood', 'TCP', '', ['u1000']),
    #Fault('ping-flood', 'PING', '', ['u1000']),
    #Fault('interrupts', 'INTR', '--sleep ', ['32']),
]
