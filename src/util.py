"""
PEER REVIEW SCRIPT: util

authors:
@markoprodanovic

last edit:
Monday, January 12, 2020
"""

from termcolor import cprint
import sys


def print_error(msg):
    """ Prints the error message without shutting down the script

    Args:
        msg (string): Message to print before continuing execution
    """
    cprint(f'\n{msg}\n', 'red')


def shut_down(msg):
    """ Shuts down the script.

    Args:
        msg (string): Message to print before printing 'Shutting down...' 
                      and exiting the script.
    """
    cprint(f'\n{msg}\n', 'red')
    print('Shutting down...')
    sys.exit()
