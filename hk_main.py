# !/user/bin/env python3

# Main module where all of the subsystems for the HK are called and activated, also allows for commandline arguments
# for debugging, showing vision and storing detections to file

import threading
from time import sleep

import hk_mission_parameteriser
import hk_ml_systems
from hk_console_logger import ConsoleAccess
from hk_event_queue import EventQueueAccess
from hk_serial_interfacing import SerialAccess
from hk_serial_to_events import serial_getter
from hk_actions import action_processor


def start_systems(show_vision=True, store_detections=False, console_logging=False):
    # Enable/Disable console printing
    ConsoleAccess.console_print_enable = console_logging

    # Start the event queue as a thread
    threading.Thread(target=EventQueueAccess.event_spout, daemon=False).start()

    # Start the mission parameteriser parameter getter as a thread
    threading.Thread(target=hk_mission_parameteriser.get_params, daemon=False).start()

    # Start the serial access reader as a thread
    threading.Thread(target=SerialAccess.read_serial, daemon=False).start()

    sleep(2)

    # Start the serial write processor as a thread
    threading.Thread(target=SerialAccess.write_serial_processor, daemon=False).start()

    sleep(2)

    # Start the serial getter function as a thread
    threading.Thread(target=serial_getter, daemon=False).start()

    sleep(2)

    threading.Thread(target=action_processor, daemon=False).start()

    sleep(2)

    # Start the mission parameteriser objective processor as a thread
    threading.Thread(target=hk_mission_parameteriser.objective_processor, daemon=False).start()

    # Start the ML systems, passing in the commandline arguments for showing vision and storing detections to file
    hk_ml_systems.start_machine_vision(show_vision, store_detections)

    # serial write test
    # todo: probably needs removing
    sleep(30)

    EventQueueAccess.queue_addition("SERIAL_WRITE", "test_serial", 1)


if __name__ == "__main__":
    # argparse handles the commandline arguments for debugging, showing vision and storing detections to file
    import argparse

    parser = argparse.ArgumentParser(description='Run a test of ML Systems, either with Vision ON or OFF')

    parser.add_argument('--no-vision', dest='v', action='store_false', help='Disables User Vision')

    parser.add_argument('--store-detections', dest='a', action='store_true', help='Enables Storing of Detected '
                                                                                  'Objects as Images under /Captured')

    parser.add_argument('--debug', dest='l', action='store_true', help='Enables Logging in Console, FPS, '
                                                                       'Detected Objects etc.')

    args = parser.parse_args()

    # Pass arguments into the start systems function
    start_systems(args.v, args.a, args.l)
