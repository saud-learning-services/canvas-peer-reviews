"""
PEER REVIEW SCRIPT: main

authors:
@markoprodanovic
@alisonmyers

last edit:
Monday, January 12, 2020
"""

import json
import time
import os
from os.path import normcase

import ipywidgets as widgets
import pandas as pd
import requests
from canvasapi import Canvas
from IPython.display import display
from IPython.lib.pretty import pretty
from termcolor import cprint
from datetime import datetime

from dataframe_builder import make_assessments_df
from interface import get_user_inputs
from util import shut_down
import settings

import pprint as pp


def main():

    # initialize global variables - call only once
    settings.init()

    # get user inputs
    inputs = get_user_inputs()

    # get rubric object
    rubric = _get_rubric(settings.course, settings.assignment)

    # get assessments JSON - details each complete assessment (could be empty)
    assessments_json = _get_assessments_json(rubric)

    # get peer reviews JSON - details each assigned review
    peer_reviews_json = _get_peer_reviews_json(
        inputs['base_url'],
        inputs['course_number'],
        inputs['assignment_number'],
        inputs['token']
    )

    # get students enrolled in course
    students = _get_students(settings.course)

    # make assessments dataframe - see docstring for schema
    assessments_df = make_assessments_df(
        assessments_json,
        peer_reviews_json,
        students,
        rubric
    )

    ###================== NOT DONE BELOW ===================###

    # CAN REFACTOR - EXTRACT
    peer_reviews_df = pd.DataFrame(peer_reviews_json)
    peer_reviews_df['Assessor'] = None

    students_json = make_json_list(students)
    students_df = pd.DataFrame(students_json)
    overview_df = make_user_table(students_df, peer_reviews_df)

    for outer_index, outer_row in overview_df.iterrows():
        num_scores_for_user = 0
        for index, row in assessments_df.iterrows():
            if row['Assessee'] == outer_row['Name']:
                num_scores_for_user += 1
                score = row[2]
                overview_df.at[outer_index,
                               f'Review: {num_scores_for_user}'] = score

    overview_df = overview_df.drop(['SID'], axis=1)

    now = datetime.now()
    date_time = now.strftime('%m:%d:%Y, %H.%M.%S')

    dir_name = f'{settings.course.name}({date_time})'
    dir_path = f'../peer_review_data/{dir_name}'
    os.mkdir(dir_path)

    output_csv(assessments_df, dir_path, "peer_review_assessments")
    output_csv(overview_df, dir_path, "peer_review_overview")
    ###================== NOT DONE ABOVE ==================###


def _get_rubric(course, assignment):
    """ Parses rubric id from assignment object. If found, retrieves rubric with that
        id from course object. Otherwise, shuts down with error message.

    Args:
        course (object): Course object - canvasapi
        assignment (object): Assignment object - canvasapi

    Returns:
        rubric: Rubric object as specified by canvasapi python wrapper
    """

    # get rubric id from assignment attributes
    # throw error and shut down if assignment has no rubric
    try:
        rubric_id = assignment.attributes['rubric_settings']['id']
    except KeyError as e:
        shut_down(f'Assignment: {assignment.name} has no rubric')

    # get rubric object from course
    rubric = course.get_rubric(
        rubric_id,
        include=['peer_assessments'],
        style='full')

    return rubric


def _get_students(course):
    """ Gets a paginated list of students enrolled in the course using the
        course param and shuts down with error if that list is empty.

    Args:
        course (object): Course object - canvasapi

    Returns:
        students: Paginated list of students in this course
    """
    students = course.get_users(enrollment_type=['student'])
    if not students:
        shut_down('ERROR: Course must have students enrolled.')

    return students


def _get_assessments_json(rubric):
    """Gets completed assessments data from rubric object. If there rubric
       object is missing assessments field, shuts down with error otherwise
       returns JSON.

    Args:
        rubric (object): Rubric object - canvasapi

    Returns:
        assessments_json: JSON data of all completed assessments
    """

    try:
        assessments_json = rubric.attributes['assessments']
    except AttributeError:
        shut_down('ERROR: Rubric JSON object has no assessments field.')

    return assessments_json


def _get_peer_reviews_json(base_url, course_id, assignment_id, token):
    """Makes request to Canvas API to get peer review object. Shuts down with
       error if server responds with error or if response is empty. Otherwise
       returns JSON.

    Args:
        base_url (str): Canvas instance being used
        course_id (str): Canvas course id
        assignment_id (str): Canvas assignment id
        token (str): Canvas access token

    Returns:
        assessments_json: peer reviews JSON obj for the given course + assignment
    """

    # headers variable for REST API calls
    headers = {
        'Authorization': 'Bearer ' + token
    }

    try:
        peer_reviews_endpoint = f'{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/peer_reviews'
        peer_reviews = requests.get(peer_reviews_endpoint, headers=headers)
        peer_reviews.raise_for_status
        peer_reviews = json.loads(peer_reviews.text)
    except Exception as e:
        shut_down(
            'ERROR: Could not get peer reviews specified course and assignment (API responded with error).')

    if not peer_reviews:
        shut_down('ERROR: Assignment must have at least one peer review assigned.')

    return peer_reviews

###================== NOT DONE BELOW ==================###


def make_json_list(object_list):
    output = []
    for object in object_list:
        output.append(object.attributes)
    return output


def output_csv(df, location, file_name):
    df.to_csv(f'{location}/{file_name}.csv', index=False)
    cprint(f'{file_name}.csv successfully created in /peer_review_data', 'green')


def make_user_table(users, peer_reviews):
    df = users[['id', 'name', 'sis_user_id']].rename(
        columns={'id': 'CanvasUserID', 'name': 'Name', 'sis_user_id': 'SID'})
    df.insert(3, 'Num Assigned Peer Reviews', None)
    df.insert(4, 'Num Completed Peer Reviews', None)
    for index, row in df.iterrows():
        lookup = lookup_reviews(row['CanvasUserID'], peer_reviews)

        # if (lookup['Assigned'] == 0):
        #     df.drop(index[index])
        # else:
        df.at[index, 'Num Assigned Peer Reviews'] = lookup['Assigned']
        df.at[index, 'Num Completed Peer Reviews'] = lookup['Completed']

    return df


def lookup_reviews(uid, peer_reviews):
    assigned_subset = peer_reviews[peer_reviews['assessor_id'] == uid]
    completed_subset = assigned_subset[assigned_subset['workflow_state'] == 'completed']

    assigned = len(assigned_subset)
    completed = len(completed_subset)

    return {
        'Assigned': assigned,
        'Completed': completed
    }
