# !/user/bin/env python3

# This tests basic calls into the queue, priority, text etc.

import hk_event_queue


def test_second_queue_access_mod():
    # these should all be same as it's calling the same instance created in the main queue module
    print(hk_event_queue.EventQueueAccess)
    hk_event_queue.EventQueueAccess.queue_addition("SECOND", "QUEUE ACCESS 4", 4)
    hk_event_queue.EventQueueAccess.queue_addition("SECOND", "QUEUE ACCESS 1", 1)
    hk_event_queue.EventQueueAccess.queue_addition("SECOND", "QUEUE ACCESS 2", 2)
    hk_event_queue.EventQueueAccess.queue_addition("SECOND", "QUEUE ACCESS 3", 3)


if __name__ == "__main__":
    test_second_queue_access_mod()
    hk_event_queue.EventQueueAccess.priority_queue.join()
