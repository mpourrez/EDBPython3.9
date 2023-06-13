#!/usr/bin/env python
# encoding: utf-8
"""
configs.py
"""

from enum import Enum
class EdgeDevice(Enum):
    RPI = 'raspberrypi'
    NANO = 'nano'
    CORAL = 'coral'

EDGE_DEVICE_NAME = EdgeDevice.RPI
if EDGE_DEVICE_NAME == EdgeDevice.RPI:
    EDGE_DEVICES_IP = ['192.168.0.168']
    PROJECT_PATH = "/home/pi/Projects/"
else:
    EDGE_DEVICES_IP = ['192.168.0.225']
    PROJECT_PATH = "/home/nano/Projects/"
EDGE_DEVICE_PORT = 50051
ORCHESTRATOR_IP = '192.168.0.22'

MAX_FRAME_NUM = 300
#PROJECT_PATH = "/Users/maryampourreza/Projects/"
WORKLOAD_INPUT_PATH = 'workloads/MOT20-01/img1/'
TIME_BOUND_FOR_FAULT_INJECTION = 5  # in-seconds

FAULT_FREE_DURATIONS = 30
NUMBER_OF_FAULT_INJECTIONS = 10
NUMBER_OF_FAULT_FREE_ROUNDS = 10
FAULT_INJECTION_DURATION = 30
RESOURCE_MONITOR_INTERVALS = 1  # in-seconds
EXPERIMENT_DURATION = FAULT_INJECTION_DURATION * NUMBER_OF_FAULT_INJECTIONS + \
                      FAULT_FREE_DURATIONS * (NUMBER_OF_FAULT_INJECTIONS + 1)

#
APPLICATIONS = ['MM', 'FFT', 'FPO-SIN', 'FPO-SQRT',
                'IP', 'SA', 'ST', 'IC-A-CPU', 'IC-S-CPU']

# APPLICATIONS = ['MM', 'FFT', 'FPO-SIN', 'FPO-SQRT', 'SORT', 'DD', 'IPERF',
#                 'IP', 'SA', 'ST', 'IC-A-CPU', 'IC-S-CPU', 'OD-CPU', 'PS', 'AE', 'OT-CPU']


class Fault:
    def __init__(self, fault_name, abbreviation, fault_command, fault_config):
        self.fault_name = fault_name
        self.abbreviation = abbreviation
        self.fault_command = fault_command
        self.fault_config = fault_config

FAULTS = [
    Fault('cpu-overload', 'CPU', '--cpu 0 --cpu-load', ['20', '60', '90']),
    Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['20%', '60%', '90%']),
    Fault('io-stress', 'IO', '--io', ['100']),
    Fault('page-fault', 'PF', '--fault', ['0']),
    Fault('cache-thrashing', 'CCHE', '--cache', ['0']),
    # Fault('context-switch', 'CTXS', '--cswitch --cswitch-ops', ['10000']),

    # Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['20%']),
    # Fault('cpu-overload', 'CPU', '--cpu 0 --cpu-load', ['80']),

    # Fault('cpu-overload', 'CPU', '--cpu 0 --cpu-load', ['20', '50', '80']),
    # # Fault('memory-contention', 'MEM', '--vm 0 --vm-method all --vm-bytes', ['20%', '60%', '90%']),
    # Fault('io-stress', 'IO', '--io', ['100']),
    # Fault('page-fault', 'PF', '--fault', ['0']),
    # Fault('cache-thrashing', 'CCHE', '--cache', ['0']),
    # Fault('context-switch', 'CTXS', '--cswitch --cswitch-ops', ['10000']),
    # Fault('interrupts', 'INTR', '--sleep ', ['32']),
    # # Fault('hdd-overload', 'HDD', '--hdd 0 --hdd-bytes', ['20%', '', '60%']),
    # Fault('ping-flood', 'TCP', '', ['u1000']),
    # Fault('ping-flood', 'PING', '', ['u1000']),
]

