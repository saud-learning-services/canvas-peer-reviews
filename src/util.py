"""
PEER REVIEW SCRIPT: util

authors:
@markoprodanovic

last edit:
Monday, January 10, 2020
"""

from termcolor import cprint


def shut_down(msg):
    """ Shuts down the script.

    Args:
        msg (string): Message to print before printing 'Shutting down...' 
                      and exiting the script.
    """
    cprint(f'\n{msg}\n', 'red')
    print('Shutting down...')
    sys.exit()
