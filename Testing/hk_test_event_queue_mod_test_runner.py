# !/user/bin/env python3

# this is designed as a test to ensure that multiple modules can be called with access to the same event queue,
# without calling a whole new instance of the event queue and all being able to drop events into the same queue;
# allowing the hk to drop in events from multiple systems with varying priorities - for instance if it has something
# in the queue to react to an image, but is about to hit something, avoiding the object will be pushed to a higher
# priority over the image processing and be handled sooner

import threading

import hk_event_queue
from Testing import hk_test_event_queue_mod_3, hk_test_event_queue_mod, hk_test_event_queue_mod_2, \
    hk_test_event_queue_mod_multiple_queues, hk_test_event_random_loop_queue_mod

# start the thread for this instance
threading.Thread(target=hk_event_queue.EventQueueAccess.event_test_spout, daemon=False).start()

# threading.Thread(target=hk_test_event_queue_mod.test_second_queue_access_mod(), daemon=True).start()
hk_test_event_queue_mod.test_second_queue_access_mod()

# also test that threaded modules also work nicely with the main event queue
threading.Thread(target=hk_test_event_queue_mod_2.test_third_queue_access_mod(), daemon=False).start()

threading.Thread(target=hk_test_event_queue_mod_3.test_fourth_queue_access_mod(), daemon=False).start()

# test that new instances of the queue can be called, to ensure multiple different queues can be run
threading.Thread(target=hk_test_event_queue_mod_multiple_queues.test_diff_queue_mod(), daemon=False).start()

threading.Thread(target=hk_test_event_random_loop_queue_mod.test_loop_queue_access_mod(), daemon=False).start()

# freeze the queue until all events have processed - this won't be necessary on an actual run as new events will be
# inserted while the overall program is still running, this just allows the queue to be processed before this python
# module ends
hk_event_queue.EventQueueAccess.priority_queue.join()
