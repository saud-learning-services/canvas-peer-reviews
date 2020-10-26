"""
PEER REVIEW SCRIPT: interface

authors:
@markoprodanovic

last edit:
Monday, January 10, 2020
"""

import getpass
import settings
from util import shut_down
from canvasapi import Canvas
from termcolor import cprint


def get_user_inputs():
    """Prompt user for required inputs. Queries Canvas API throughout to check for
    access and validity errors. Errors stop execution and print to screen.

    Returns:
        Dictionary containing inputs
    """

    # prompt user for url and token
    url = input('Canvas Instance URL: ')
    token = getpass.getpass('Please enter your token: ')

    # Canvas object to provide access to Canvas API
    canvas = Canvas(url, token)

    # get user object
    try:
        user = canvas.get_user('self')
        cprint(f'\nHello, {user.name}!', 'green')
        # pp.pprint(user.attributes)
        # shut_down('TEMP KILL SWITCH')
    except Exception as e:
        shut_down(
            """
            ERROR: could not get user from server.
            Please ensure token is correct and valid and ensure using the correct instance url.
            """
        )

    # get course object
    try:
        course_number = input('Course Number: ')
        course = canvas.get_course(course_number)
    except Exception as e:
        shut_down('ERROR: Course not found. Please check course number.')

    # get assignment object
    try:
        assignment_number = input('Assignment Number: ')
        assignment = course.get_assignment(assignment_number)
    except Exception as e:
        shut_down('ERROR: Assignment not found. Please check assignment number.')

    # prompt user for confirmation
    _prompt_for_confirmation(user.name, course.name, assignment.name)

    # set course and assignment objects to global variables
    settings.course = course
    settings.assignment = assignment

    # return inputs dictionary
    return {
        'token': token,
        'base_url': url,
        'course_number': course_number,
        'assignment_number': assignment_number
    }


def _prompt_for_confirmation(user_name, course_name, assignment_name):
    """Prints user inputs to screen and asks user to confirm. Shuts down if user inputs
    anything other than 'Y' or 'y'. Returns otherwise.

    Args:
        user_name (string): name of user (aka. holder of token)
        course_name (string): name of course returned from Canvas
        assignment_name (string): name of assignment returned from Canvas

    Returns:
        None -- returns only if user confirms

    """
    cprint('\nConfirmation:', 'blue')
    print(f'USER:  {user_name}')
    print(f'COURSE:  {course_name}')
    print(f'ASSIGNMENT:  {assignment_name}')
    print('\n')

    confirm = input(
        'Would you like to continue using the above information?[y/n]: ')

    print('\n')

    if confirm == 'y' or confirm == 'Y':
        return
    elif confirm == 'n' or confirm == 'N':
        shut_down('Exiting...')
    else:
        shut_down('ERROR: Only accepted values are y and n')
