# !/user/bin/env python3

# This tests continued access of the queue ensuring that newer inserts into the queue are handled properly

import random
import threading

import hk_event_queue


def test_loop_queue_access_mod():
    # these should all be same as it's calling the same instance created in the main queue module
    print(hk_event_queue.EventQueueAccess)

    for i in range(1, 50):
        random_event_no = random.randint(1, 4)
        hk_event_queue.EventQueueAccess.queue_addition("CONTINUED", "QUEUE ACCESS " + str(i),
                                                       random_event_no)


if __name__ == "__main__":
    threading.Thread(target=test_loop_queue_access_mod(), daemon=False).start()
    hk_event_queue.EventQueueAccess.priority_queue.join()
