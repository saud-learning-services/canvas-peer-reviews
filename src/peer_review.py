"""
PEER REVIEW SCRIPT: main

authors:
@markoprodanovic
@alisonmyers

last edit:
Monday, January 10, 2020
"""

import json
import time
import os
from os.path import normcase
import settings

import ipywidgets as widgets
import pandas as pd
import requests
from canvasapi import Canvas
from IPython.display import display
from IPython.lib.pretty import pretty
from termcolor import cprint
from datetime import datetime

from interface import get_user_inputs
from util import shut_down


def main():

    # initialize global variables - call only once
    settings.init()

    # get user inputs
    inputs = get_user_inputs()

    # get rubric object
    rubric = _get_rubric(settings.course, settings.assignment)

    # get assessments JSON - details each complete assessment
    assessments_json = rubric.attributes['assessments']

    # get peer reviews JSON - details each assigned review
    peer_reviews_json = get_canvas_peer_reviews(
        inputs['base_url'],
        inputs['course_number'],
        inputs['assignment_number'],
        inputs['token']
    )

    # get students enrolled in course
    students = settings.course.get_users(enrollment_type=['student'])

    ###================== NOT DONE BELOW ===================###
    ap_table = make_assessments_pairing_table(
        assessments_json, peer_reviews_json, students, rubric)

    # CAN REFACTOR - EXTRACT
    peer_reviews_df = make_peer_reviews_df(peer_reviews_json)
    peer_reviews_df['Assessor'] = None

    students_json = make_json_list(students)
    students_df = pd.DataFrame(students_json)
    overview_df = make_user_table(students_df, peer_reviews_df)

    for outer_index, outer_row in overview_df.iterrows():
        num_scores_for_user = 0
        for index, row in ap_table.iterrows():
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

    output_csv(ap_table, dir_path, "peer_review_assessments")
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

    # try:
    #     users = course.get_users(enrollment_type=['student'])
    #     rubric_id = assignment.attributes['rubric_settings']['id']
    # except KeyError as e:
    #     msg = str(e)
    #     shut_down(f'Assignment: {assignment.name} has no rubric')
    # except Exception as e:
    #     msg = str(e)
    #     shut_down(msg)

    # rubric = course.get_rubric(
    #     rubric_id,
    #     include=['peer_assessments'],
    #     style='full')
    # assessments_json = rubric.attributes['assessments']

    # peer_reviews_json = get_canvas_peer_reviews(
    #     inputs['base_url'], inputs['course_number'], inputs['assignment_number'], inputs['token'])


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


def make_assessments_pairing_table(assessments_json, peer_reviews_json, users, rubric):
    points_possible = rubric.points_possible
    peer_reviews_df = make_peer_reviews_df(peer_reviews_json)
    peer_reviews_df['Assessor'] = None
    peer_reviews_df['Assessee'] = None
    peer_reviews_df = peer_reviews_df[
        ['Assessee', 'Assessor', 'user_id', 'assessor_id', 'asset_id']]
    assessments_df = make_assessments_df(assessments_json)[
        ['assessor_id', 'artifact_id', 'data', 'score']]
    assessments_df = expand_items(assessments_df, rubric.data)
    assessments_df = assessments_df.rename(
        columns={'score': f'Total Score ({points_possible})'})

    merged_df = pd.merge(peer_reviews_df, assessments_df,
                         how='left',
                         left_on=['assessor_id', 'asset_id'],
                         right_on=['assessor_id', 'artifact_id'])

    merged_df = merged_df.drop(['asset_id', 'artifact_id'], axis=1)

    for index, row in merged_df.iterrows():
        merged_df.at[index, 'Assessor'] = user_lookup(
            row['assessor_id'], users)
        merged_df.at[index, 'Assessee'] = user_lookup(
            row['user_id'], users)

    merged_df = merged_df.drop(['user_id', 'assessor_id'], axis=1)

    return merged_df


def user_lookup(key, users):
    for user in users:
        if key == user.id:
            return user.name

    return 'Not Found'


def expand_items(assessments_df, list_of_rubric_criteria):
    pd.options.mode.chained_assignment = None  # default='warn'
    # print(len(completed_reviews_df[0]['Score by Rubric Item']))
    for index, row in assessments_df.iterrows():

        item_num = 1
        for item in row['data']:
            value = item['points']
            col = item['criterion_id']
            assessments_df.at[index, col] = value
            # reviews_df.at[index, 'Item ' + str(item_num)] = item['points']
            # print(str(index) + ' ' + str(item_num) + ": " + str(item['points']))
            item_num += 1

    new_names = {}
    for crit in list_of_rubric_criteria:
        crit_id = crit['id']
        crit_description = crit['description']
        crit_points = crit['points']
        new_names[crit_id] = f"{crit_description} ({crit_points})"

    assessments_df = assessments_df.rename(columns=new_names)
    del assessments_df['data']

    return assessments_df


def get_canvas_peer_reviews(base_url, course_id, assignment_id, token):

     # headers variable for REST API calls
    headers = {
        'Authorization': 'Bearer ' + token
    }

    try:
        peer_reviews_endpoint = f'{base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/peer_reviews'
        peer_reviews = requests.get(peer_reviews_endpoint, headers=headers)
        peer_reviews.raise_for_status
        peer_reviews = json.loads(peer_reviews.text)
        return peer_reviews
    except Exception as e:
        shut_down(
            'ERROR: Could not retrieve peer reviews for specified course and assignment')


def make_assessments_df(assessments):
    if not assessments:
        shut_down(
            'Error: there must be at least one completed assessment for the given rubric.')

    for value in assessments:
        to_delete = value['rubric_association']
        del to_delete['summary_data']

    return pd.DataFrame(assessments)


def make_peer_reviews_df(peer_reviews):
    df = pd.DataFrame(peer_reviews)
    # df['user_id'] = df['user_id'].astype(str)

    return df
