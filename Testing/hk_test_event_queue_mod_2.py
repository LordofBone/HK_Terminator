# !/user/bin/env python3

# This tests that multiple modules can access the same queue and it will work correctly

import hk_event_queue


def test_third_queue_access_mod():
    print(hk_event_queue.EventQueueAccess)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED THIRD", "QUEUE ACCESS 3", 3)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED THIRD", "QUEUE ACCESS 4", 4)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED THIRD", "QUEUE ACCESS 1", 1)
    hk_event_queue.EventQueueAccess.queue_addition("THREADED THIRD", "QUEUE ACCESS 2", 2)


if __name__ == "__main__":
    test_third_queue_access_mod()
    hk_event_queue.EventQueueAccess.priority_queue.join()
