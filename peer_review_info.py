# -*- coding: utf-8 -*-
"""
PEER REVIEW SCRIPT

authors:
@alisonmyers
@markoprodanovic

last edit:
Monday, November 11, 2019
"""
import json
import ipywidgets as widgets

import pandas as pd
import requests

from helpers import make_assessment_df, make_peer_review_df, shut_down, make_output_tables


def peer_review(inputs):
    # prompts user for inputs via terminal
    # asks for Canvas token, Canvas instance (url), course id, assignment_id
    # inputs = get_user_inputs()

    token = inputs['token']
    base_url = inputs['base_url']
    course = inputs['course_number']
    asmt_id = inputs['assignment_number']

    # headers variable for REST API calls
    headers = {
        'Authorization': 'Bearer ' + token
    }

    # Query Canvas LMS REST API - get assignment, rubric and peer review information
    # HTTPErrors will be caught and halt execution of the script
    try:
        ##### ASSIGNMENT REQUEST #####
        assignment_endpoint = f'{base_url}/api/v1/courses/{course}/assignments/{asmt_id}'
        assignment = requests.get(assignment_endpoint, headers=headers)
        assignment.raise_for_status()
        assignment = json.loads(assignment.text)
        # pprint.pprint(assignment)
        # =============================

        ####### RUBRIC REQUEST #######
        rubric_id = str(assignment['rubric_settings']['id'])
        payload = {'include': 'peer_assessments', 'style': 'full'}
        rubric_endpoint = f'{base_url}/api/v1/courses/{course}/rubrics/{rubric_id}'
        rubric = requests.get(rubric_endpoint, params=payload, headers=headers)
        rubric.raise_for_status
        rubric = json.loads(rubric.text)
        # pprint.pprint(rubric['assessments'])
        # =============================

        ##### PEER REVIEW REQUEST #####
        peer_review_endpoint = f'{base_url}/api/v1/courses/{course}/assignments/{asmt_id}/peer_reviews'
        peer_review = requests.get(peer_review_endpoint, headers=headers)
        peer_review.raise_for_status
        peer_review = json.loads(peer_review.text)
        # pprint.pprint(peer_review)
        # =============================

        ######## USER REQUEST ########
        users_endpoint = f'{base_url}/api/v1/courses/{course}/users'
        payload = {'per_page': 1000}
        users = requests.get(users_endpoint, params=payload, headers=headers)
        users.raise_for_status
        users = json.loads(users.text)
        # pprint.pprint(users)
        # =============================
    except requests.exceptions.HTTPError as e:
        print('Request Error:')
        print('Check token is correct and active. Check course id, assignment id, and canvas instance are correct.')
        shut_down(str(e))
    except KeyError as e:
        shut_down(
            '"rubric_settings" key not found in API response. Check to see if requested assignment has associated rubric. Note that this script will not for non peer-reviewed assignments')
    except Exception as e:
        shut_down(str(e))

    # pprint.pprint(rubric['assessments'])
    # pprint.pprint(peer_review)

    # convert JSON objects into pandas dataframesc
    assessments_df = make_assessment_df(rubric['assessments'])
    peer_review_df = make_peer_review_df(peer_review)
    users_df = pd.DataFrame(users)

    make_output_tables(peer_review_df, assessments_df, users_df,
                       course, assignment['points_possible'])

    print('Tables successfully built in /data folder!')


def display_url_selector():
    CANVAS_INSTANCES = ['https://canvas.ubc.ca',
                        'https://ubc.instructure.com',
                        'https://ubc.test.instructure.com',
                        'https://ubcsandbox.instructure.com']

    url_selector = widgets.Dropdown(
        options=CANVAS_INSTANCES,
        value='https://canvas.ubc.ca',
        description='Instance:',
        disabled=False,
    )

    display(url_selector)
