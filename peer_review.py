import getpass
import ipywidgets as widgets
from canvasapi import Canvas
from IPython.display import display
from IPython.lib.pretty import pretty
from termcolor import cprint
from peer_review_info import peer_review

CANVAS_INSTANCES = ['https://canvas.ubc.ca',
                    'https://ubc.instructure.com',
                    'https://ubc.test.instructure.com',
                    'https://ubcsandbox.instructure.com']


def get_user_inputs():

    token = getpass.getpass('Please enter your token: ')
    url = input('Canvas Instance URL: ')
    canvas = Canvas(url, token)

    try:
        user = canvas.get_user('self')
        cprint(f'\nHello, {user.name}!', 'green')
    except Exception as e:
        cprint('ERROR: could not get user from server. Please ensure token is correct and valid and ensure using the correct instance url.', 'red')
        return
    try:
        course_number = input('Course Number: ')
        course = canvas.get_course(course_number)
    except Exception as e:
        cprint('ERROR: Course not found. Please check course number.', 'red')
        return
    try:
        assignment_number = input('Assignment Number: ')
        assignment = course.get_assignment(assignment_number)
    except Exception as e:
        cprint('ERROR: Assignment not found. Please check assignment number.', 'red')
        return

    cprint('\nConfirmation:', 'blue')
    print(f'USER:  {user.name}')
    print(f'COURSE:  {course.name}')
    print(f'ASSIGNMENT:  {assignment.name}')
    print('\n')

    confirm = input(
        'Would you like to continue using the above information?[y/n]: ')

    if confirm is 'n':
        cprint('Exiting', 'red')
        return
    elif confirm is 'y':
        inputs = {
            'token': token,
            'base_url': url,
            'course_number': course_number,
            'assignment_number': assignment_number
        }
        peer_review(inputs)
    else:
        cprint('ERROR: Only accepted values are y and n', 'red')
        return

    print('poo')
