# !/user/bin/env python3

# This sets up and tests multiple queues

import threading
import hk_event_queue


def test_diff_queue_mod():
    # should match the instance of the other EventQueueAccess calls
    print(hk_event_queue.EventQueueAccess)
    NewQueue = hk_event_queue.EventQueue()
    NewQueue2 = hk_event_queue.EventQueue()
    # these two should have difference instance id's from the above and from each other
    print(NewQueue)
    print(NewQueue2)
    hk_event_queue.EventQueueAccess.queue_addition("MORE", "QUEUE ACCESS 1", 1)
    hk_event_queue.EventQueueAccess.queue_addition("MORE", "QUEUE ACCESS 3", 3)
    NewQueue.queue_addition("1ST NEW", "QUEUE 1", 1)
    NewQueue.queue_addition("1ST NEW", "QUEUE 3", 3)
    NewQueue2.queue_addition("2ND NEW", "QUEUE 4", 4)
    NewQueue2.queue_addition("2ND NEW", "QUEUE 2", 2)

    # start the thread for 1st new queue
    threading.Thread(target=NewQueue.event_test_spout, daemon=False).start()

    # start the thread for 2nd new queue
    threading.Thread(target=NewQueue2.event_test_spout, daemon=False).start()


if __name__ == "__main__":
    test_diff_queue_mod()
    hk_event_queue.EventQueueAccess.priority_queue.join()
