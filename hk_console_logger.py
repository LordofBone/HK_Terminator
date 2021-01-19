# !/user/bin/env python3

# This is to allow debugging, instead of using 'print' for getting debug information on runtime, this is a cleaner
# solution where you can just add in ConsoleAccess.console_printer(text) and it will only print if the console
# printer is set to True; allowing for a debug mode
# todo: probably need to replace this at some point with a proper logger
from dataclasses import dataclass


@dataclass
class PrintConsole(object):
    # Because this is a dataclass this bool can be accessed easily from the class instantiation,
    # eg: ConsoleAccess.console_print_enable = True
    console_print_enable: bool = False

    def console_printer(self, text):
        if self.console_print_enable:
            print(text)


# Instantiate the class so that it can be imported and used by all modules
ConsoleAccess = PrintConsole()

if __name__ == "__main__":
    # Test console logging system works
    ConsoleAccess.console_print_enable = True
    ConsoleAccess.console_printer("Test SUCCESS!")
