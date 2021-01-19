# !/user/bin/env python3

# This is for user control of the HK
# todo: determine is this is required and add to it to allow more direct controls over the HK

import qprompt

from hk_main import start_systems

# setup menu library
menu = qprompt.Menu()


# todo: stuff for shutting down systems and clearing up stuff will go here
def clear_down():
    pass


# menu setup and display
try:
    menu.add("1", "Start Systems With Vision", start_systems())
    # qprompt.echo("Current Status:")
    # qprompt.echo(EventQueueAccess.get_latest_event())

    menu.main(loop=True)
except KeyboardInterrupt:
    clear_down()

if __name__ == "__main__":
    pass
