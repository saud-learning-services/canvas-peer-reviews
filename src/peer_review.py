"""
PEER REVIEW SCRIPT: main

authors:
@markoprodanovic
@alisonmyers

last edit:
Monday, January 14, 2020
"""

from datetime import datetime
from pathlib import Path
from os.path import normcase
from canvasapi import Canvas
from termcolor import cprint
import pandas as pd
import requests
from pprint import pprint
import time
import json
import os

from dataframe_builder import make_assessments_df, make_overview_df
from interface import get_user_inputs
from util import shut_down
import settings

# used to print formatted JSON to jupyter (for testing)
import pprint as pp


def main():

    # get user inputs
    inputs = get_user_inputs()

    # get rubric object
    rubric = _get_rubric(settings.COURSE, settings.ASSIGNMENT)

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
    students = _get_students(settings.COURSE)

    # make assessments dataframe - see docstring for schema
    assessments_df = make_assessments_df(
        assessments_json,
        peer_reviews_json,
        students,
        rubric
    )

    # make overview dataframe - see docstring for schema
    overview_df = make_overview_df(assessments_df, peer_reviews_json, students)

    # output the dataframes to csv's in /peer_review_data directory
    _create_output_tables(assessments_df, overview_df)


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
        rubric_id = assignment.rubric_settings['id']

        # depreciated sytax - remove soon
        # rubric_id = assignment.attributes['rubric_settings']['id']
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
        assessments_json = rubric.assessments

        # depreciated sytax - remove soon
        # assessments_json = rubric.attributes['assessments']
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


def _create_output_tables(assessments_df, overview_df):
    """ Outputs dataframes to .csv files in /peer_review_data directory

    Args:
        assessments_df (DataFrame): Assessments table for output
        overview_df (DataFrame): Overview table for output

    """
    now = datetime.now()
    date_time = now.strftime('%m:%d:%Y, %H.%M.%S')

    dir_name = f'{settings.COURSE.name}, {settings.ASSIGNMENT.name} ({date_time})'
    dir_path = Path(f'./peer_review_data/{dir_name}')
    os.mkdir(dir_path)

    _output_csv(assessments_df, dir_path, "peer_review_assessments")
    _output_csv(overview_df, dir_path, "peer_review_overview")


def _output_csv(df, location, file_name):
    """ Writes CSV to location with file_name

    Args:
        df (DataFrame): Table to output
        location (string): filepath to output directory
        file_name (string): name to give file "example" => "example.csv"
    """
    df.to_csv(f'{location}/{file_name}.csv', index=False)
    cprint(f'{file_name}.csv successfully created in /peer_review_data', 'green')

if __name__ == "__main__":
    main()