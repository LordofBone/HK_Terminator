# !/user/bin/env python3
# Available commands to write to the low-level systems:
# Does a test run where the HK will move around a bit to test motors and avoidance routines:
# "run_test"

# Measures distance from all the ultrasonics and returns the results:
# "measure_dist"

# Moves the HK forward
# "move_forward"

# Moves the HK backward
# "move_backward"

# Turns the HK right
# "turn_right"

# Turns the HK left
# "turn_left"

# Turns on patrol mode, where the bot will move around in a patrol pattern for a time:
# "patrol_mode"

# Switches movement override on (the HK can not be moved without ultrasonics being clear)
# "move_override_on"

# Switches movement override of (the HK can be moved ignoring all ultrasonics)
# "move_override_off"

# Fires purple plasma
# "plasma_purple"

# Fires red plasma
# "plasma_red"

import threading
from dataclasses import dataclass, field
from time import sleep

import serial

from hk_console_logger import ConsoleAccess
from hk_yaml_importer import YAMLAccess
from hk_event_processor import EventFactoryAccess


# todo: determine whether this needs to be a dataclass
@dataclass
class SerialController:
    # Boolean that indicates whether serial is active or not
    serial_on: bool = False

    # List of serial events
    serial_list: list = field(default_factory=list)

    def __post_init__(self):
        # Configure serial from the settings in serial_config.yaml
        self.s1 = serial.Serial()
        self.s1.baudrate = YAMLAccess.SPEED
        self.s1.port = YAMLAccess.PORT

        # Attempt to open the serial port with the above configuration
        self.open_serial()

    # Get items from the serial output list
    def get_serial_list(self):
        try:
            # Pop 0 index so that it's FIFO rather than LIFO like the event handling as these want to be processed
            # in-order rather than latest first
            event_popped = self.serial_list.pop(0).strip()
        except IndexError:
            event_popped = ""
        return event_popped

    # This will try and open the serial port and will set the serial_on boolean as appropriate
    def open_serial(self):
        try:
            self.s1.open()
            self.serial_on = True
            ConsoleAccess.console_printer("Serial Connection SUCCESS")
        except serial.serialutil.SerialException:
            self.s1.close()
            self.serial_on = False
            ConsoleAccess.console_printer("Serial Connection FAILURE")

    # This grabs the serial writes from the event factory and will write them to the Arduino
    # todo: upon a write
    #  failure this will simply move onto the next serial writes until a connection is found, may need to add in
    #  re-attempts? This is setup to grab from the event factory list, so that the event queue handles them one at a
    #  time, to prevent multiple conflicting writes, if you want to write something to serial a "SERIAL_WRITE" event
    #  is needed, along with the serial instruction to be sent
    def write_serial_processor(self):
        while True:
            s_write = EventFactoryAccess.get_serial_list_to_write()
            if not s_write == "":
                self.write_serial(s_write)
            else:
                sleep(1)

    # This is where all serial writes to the Arduino are handled, it will also check if the serial fails and set a
    # retry of the serial open and wait if so (wait time configurable in serial_config.yaml)
    def write_serial(self, to_write):
        if self.s1.is_open:
            final_write = to_write + "\n"
            try:
                self.s1.write(final_write.encode())
            except serial.serialutil.SerialException:
                self.open_serial()
                sleep(YAMLAccess.S_WAIT)
        else:
            ConsoleAccess.console_printer("No Serial on WRITE - Retrying Connection")
            self.open_serial()
            sleep(YAMLAccess.S_WAIT)

    # This is called and threaded to read the serial outputs from the Arduino and will append them to the read serial
    # list - this will also try the serial connection and if it fails it will attempt to re-open the connection and
    # wait if so (wait time configurable in serial_config.yaml)
    def read_serial(self):
        while True:
            if self.s1.is_open:
                ConsoleAccess.console_printer("Reading Serial")
                try:
                    current_serial = self.s1.readline().decode()
                except serial.serialutil.SerialException:
                    current_serial = ""
                    self.open_serial()
                    sleep(YAMLAccess.S_WAIT)
                if not current_serial == "":
                    ConsoleAccess.console_printer(current_serial)
                    self.serial_list.append(current_serial)
            else:
                ConsoleAccess.console_printer("No Serial on READ - Retrying Connection")
                self.open_serial()
                sleep(YAMLAccess.S_WAIT)


# Instantiate the class so serial interface can be accessed from other modules
SerialAccess = SerialController()

if __name__ == "__main__":
    # Run a test on serial reads and writes
    ConsoleAccess.console_print_enable = True

    ConsoleAccess.console_printer("Testing Serial Read:")
    threading.Thread(target=SerialAccess.read_serial, daemon=False).start()
    sleep(2)

    ConsoleAccess.console_printer("Testing Serial Write:")
    # Using direct access to the write function here for testing purposes - in real world modules should use the
    # queue with event type SERIAL_WRITE" to prevent two modules from trying to write to the serial at the same time
    SerialAccess.write_serial('test_serial')

    sleep(1)

    # Test getting distance details from the Arduino
    SerialAccess.write_serial('measure_dist')

    sleep(3)

    # Print out all the serial outputs from the Arduino
    ConsoleAccess.console_printer("Testing Serial List Processing:")

    while True:
        serial_out = SerialAccess.get_serial_list()
        if serial_out == "":
            break
        else:
            ConsoleAccess.console_printer(serial_out + "\n")
        sleep(1)

    ConsoleAccess.console_printer("Serial List Test Complete")
