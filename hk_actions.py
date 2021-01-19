# !/user/bin/env python3

# High-level access for actions, such as 'terminate' where actions can be performed sequentially as well as calling
# further actions and analysis higher up the chain (like adding in further events into the event queue)

from hk_console_logger import ConsoleAccess
from hk_movements import MovementAccess
from hk_event_processor import EventFactoryAccess
from time import sleep


def action_processor():
    while True:
        # Grab the latest objective from the factory list
        action = EventFactoryAccess.get_action_list()
        # If an objective is present from the list then process it and console print
        if not action == "":
            ConsoleAccess.console_printer(action)

            # Call the relevant action
            if action == "LOCK":
                lock_movement()
            elif action == "UNLOCK":
                unlock_movement()
            elif action == "TERMINATE":
                terminate()
            elif action == "PATROL":
                patrol()
            else:
                ConsoleAccess.console_printer("unknown objective")

        # Wait for a period of time as defined in mission_parameters.yaml before processing next objective
        # todo: need to add in the above time into the YAML
        sleep(1)


def terminate():
    ConsoleAccess.console_printer("terminating subject")
    # MovementAccess.move_forward()
    MovementAccess.fire_purple_plasma()


def patrol():
    ConsoleAccess.console_printer("patrolling")
    MovementAccess.patrol_mode()


def lock_movement():
    ConsoleAccess.console_printer("locking movement")
    MovementAccess.movement_lock()


def unlock_movement():
    ConsoleAccess.console_printer("unlocking movement")
    MovementAccess.movement_unlock()
