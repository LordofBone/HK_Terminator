# !/user/bin/env python3

# This is another test that will be threaded to test multiple modules accessing the queue at the same time

import hk_event_queue


def test_fourth_queue_access_mod():
    print(hk_event_queue.EventQueueAccess)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED FOURTH AFTER JOIN", "QUEUE ACCESS 1", 1)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED FOURTH AFTER JOIN", "QUEUE ACCESS 3", 3)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED FOURTH AFTER JOIN", "QUEUE ACCESS 2", 2)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED FOURTH AFTER JOIN", "QUEUE ACCESS 4", 4)


if __name__ == "__main__":
    test_fourth_queue_access_mod()
    hk_event_queue.EventQueueAccess.priority_queue.join()
