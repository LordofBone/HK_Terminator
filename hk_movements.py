# !/user/bin/env python3

# This is where movements are called and sent to serial writes to go to the HK low-level systems (Arduino)
# All movements and low level actions are handled here

from dataclasses import dataclass
from threading import Timer
from hk_event_queue import EventQueueAccess


@dataclass
class Movement:
    # Override boolean - this is what can be set and sent to the Arduino to allow the higher-level systems to
    # override the lower-level systems (to move even when there are ultrasonic range detections)
    override: bool = False

    # The moving bool is set for a certain time after a movement command and when the lower-level systems are moving
    # the HK (to prevent multiple conflicting move calls at once)
    moving: bool = False

    # Call for forward movement
    def move_forward(self):
        if not self.moving or self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'move_forward', 1)
            self.movement_lock()

    # Call for backward movement
    def move_backward(self):
        if not self.moving or self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'move_backward', 1)
            self.movement_lock()

    # Call to turn right
    def turn_right(self):
        if not self.moving or self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'turn_right', 1)
            self.movement_lock()

    # Call to turn left
    def turn_left(self):
        if not self.moving or self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'turn_left', 1)
            self.movement_lock()

    # Activate patrol mode - where the low-level systems will move the HK in a patrol-pattern
    def patrol_mode(self):
        if not self.moving or self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'patrol_mode', 3)
            self.movement_lock()

    # Activate movement override
    def movement_override(self):
        if self.override:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'move_override_off', 2)
        else:
            EventQueueAccess.queue_addition("SERIAL_WRITE", 'move_override_on', 2)
        self.override = not self.override

    # Activates the red plasma (RGB LED's on the Arduino)
    def fire_red_plasma(self):
        EventQueueAccess.queue_addition("SERIAL_WRITE", 'plasma_red', 1)

    # Activates the purple plasma (RGB LED's on the Arduino)
    def fire_purple_plasma(self):
        EventQueueAccess.queue_addition("SERIAL_WRITE", 'plasma_purple', 1)

    # Locks movement for 3 seconds, preventing conflicting multiple movement calls
    def movement_lock(self):
        self.moving = True
        # will call the movement unlock function after 3 seconds, preventing 'double' movement commands from happening
        t = Timer(3.0, self.movement_unlock)
        t.start()

    # Unlocks movements
    def movement_unlock(self):
        self.moving = False


# Instantiate the movement class so that other modules can import and use
MovementAccess = Movement()
