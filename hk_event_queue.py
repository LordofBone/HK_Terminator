# !/user/bin/env python3

# This module is for inserting priority-based events into a queue that is called and can perform actions from these
# events; the HK project has been designed with threading in mind. Prior projects have been 1 action at a time,
# this project will be able to do multiple things at once, such as detect a face and perform actions as well as
# process movements - this is where the event queue comes in, instead of just doing direct calls to modules to
# perform actions anything that needs doing will be passed into this queue and processed one at a time (highest
# priority first, lower the number the higher the priority). Multiple threaded modules running all at once will have
# access to this queue and so will be able to pass their results and requests into it

import threading
from queue import PriorityQueue
from time import sleep

from hk_console_logger import ConsoleAccess
from hk_event_processor import EventFactoryAccess


# todo: determine whether this needs to be a dataclass
class EventQueue:
    # Initialise the queue using PriorityQueue
    def __init__(self):
        self.event_out = ["null_event", "should never see this"]

        self.priority_queue = PriorityQueue(
            maxsize=0)  # we initialise the PQ class instead of using a function to operate upon a list.

    # Function for adding events in, add the type, content and priority
    def queue_addition(self, event_type, event_content, priority=3):
        self.priority_queue.put((priority, event_type, event_content))

    # Get the latest event from the queue; grabbing the type, content - will grab the highest priority first (lower
    # the number, the higher the priority)
    def get_latest_event(self):
        self.event_out = self.priority_queue.get()[1:3]
        return self.event_out

    # The event spout is threaded out and called from higher modules, sends events out to the event processor
    def event_spout(self):
        while True:
            current_event = self.priority_queue.get()
            ConsoleAccess.console_printer(current_event)
            EventFactoryAccess.event_receiver(current_event)

    # Test spout functions the same as the normal spout but has a delay in the loop to make it easier to read when
    # testing
    def event_test_spout(self):
        while True:
            current_event = self.priority_queue.get()
            ConsoleAccess.console_printer(current_event)
            sleep(1)


# get an instance of the EventQueue class that can be accessed from other modules, this ensures that every module
# accessing will use the same instance
EventQueueAccess = EventQueue()

# when this module is called on its own run a quick test, check 'Testing' folder for more tests around this
if __name__ == "__main__":
    ConsoleAccess.console_print_enable = True
    # start the thread for this instance
    threading.Thread(target=EventQueueAccess.event_test_spout, daemon=False).start()

    # testing the main event queue that will be used by other modules in the overall system
    EventQueueAccess.queue_addition("ACCESS", "BASIC TEST 2", 2)
    EventQueueAccess.queue_addition("ACCESS", "BASIC TEST 3", 3)
    EventQueueAccess.queue_addition("ACCESS", "BASIC TEST 4", 4)
    EventQueueAccess.queue_addition("ACCESS", "BASIC TEST 1", 1)

    # Freeze the queue to prevent the program from exiting out before all events are processed - this isn't required
    # when the main program is running
    EventQueueAccess.priority_queue.join()
