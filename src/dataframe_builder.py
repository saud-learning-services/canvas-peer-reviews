"""
PEER REVIEW SCRIPT: dataframe_builder

authors:
@markoprodanovic

last edit:
Monday, January 14, 2020
"""

import math
import pprint as pp
import pandas as pd
from util import shut_down


def make_assessments_df(assessments_json, peer_reviews_json, users, rubric):
    """ Makes assessments dataframe with following schema:

    ~~COLUMNS~~
    Assessee: Name of the student who's work is being evaluated.
    Assessor: Name of the student who is evaluating the assessee.
    Total Score ({points_possible}): The total score given by the assessor 
                                    to the assessee, where points possible 
                                    is the maximum possible score for the 
                                    assignment.
    {criteria_description} ({criteria_points}): The score breakdown per criteria 
                                    item as they appear in the rubric. Will be 
                                    as many columns as criteria items in rubric 
                                    (1...n). criteria_description will be the 
                                    the heading of a single rubric item and 
                                    criteria_points is the maximum possible 
                                    score for that item.

    Args:
        assessments_json (JSON): Completed assessments
        peer_reviews_json (JSON): Assigned peer reviews
        users (list of User - canvasapi): List of User obj
        rubric (Rubric - canvasapi): Rubric obj

    Returns:
        assessments_df (DataFrame): Dataframe representing the assessments
                                    output table.
    """
    peer_reviews_df = pd.DataFrame(peer_reviews_json)
    peer_reviews_df = peer_reviews_df[['user_id', 'assessor_id', 'asset_id']]
    peer_reviews_df['Assessor'] = None
    peer_reviews_df['Assessee'] = None

    points_possible = rubric.points_possible

    if not assessments_json:
        # make table with no assessment data (empty cells)
        for crit in rubric.data:
            crit_description = crit['description']
            crit_points = crit['points']
            column_name = f"{crit_description} ({crit_points})"
            peer_reviews_df[column_name] = None
            assessments_df = peer_reviews_df.drop(['asset_id'], axis=1)
    else:
        # make completed assessments DataFrame
        completed_assessments_df = pd.DataFrame(assessments_json)[
            ['assessor_id',
             'artifact_id',
             'data',
             'score']
        ]
        completed_assessments_df = _expand_criteria_to_columns(
            completed_assessments_df,
            rubric.data
        )
        completed_assessments_df = completed_assessments_df.rename(
            columns={
                'score': f'Total Score ({points_possible})'
            })
        merged_df = pd.merge(peer_reviews_df, completed_assessments_df,
                             how='left',
                             left_on=['assessor_id', 'asset_id'],
                             right_on=['assessor_id', 'artifact_id'])
        assessments_df = merged_df.drop(['asset_id', 'artifact_id'], axis=1)

    for index, row in assessments_df.iterrows():
        assessments_df.at[index, 'Assessor'] = _user_lookup(
            row['assessor_id'], users)
        assessments_df.at[index, 'Assessee'] = _user_lookup(
            row['user_id'], users)

    assessments_df = assessments_df.drop(['user_id', 'assessor_id'], axis=1)

    return assessments_df


def make_overview_df(assessments_df, peer_reviews_json, students):
    """Makes overview dataframe with following schema:

    ~~COLUMNS~~
    Canvas User ID: The user id of the student as it appears on Canvas.
    Name: The student's name
    Num Assigned Peer Reviews: The number of peer reviews that have been assigned to the student.
    Num Completed Peer Reviews: The number of peer reviews that have been completed by the student.
    Review: review_number: The score the student has been awarded from a single peer review 
            (blank if review is not complete). Will be as many columns as there are completed 
            peer reviews for a particular student (1...n) review_number will count up from 1 
            to help identify one review from another.

    Args:
        assessments_df (DataFrame): Completed assessments
        peer_reviews_json (JSON): Assigned peer reviews
        students (list of Student - canvasapi): list of Student obj

    Returns:
        overview_df (DataFrame):
    """
    peer_reviews_df = pd.DataFrame(peer_reviews_json)
    students_df = _make_students_df(students)

    # make dataframe detailing # assigned, # completed peer reviews per student
    overview_df = _make_assigned_completed_df(students_df, peer_reviews_df)

    # for each student check if they have any complete reviews and if so,
    # add a column "Review #" and set the cell value to their score
    for outer_index, outer_row in overview_df.iterrows():
        num_scores_for_user = 0
        for index, row in assessments_df.iterrows():
            if row['Assessee'] == outer_row['Name'] and row[2] is not None:
                num_scores_for_user += 1
                score = row[2]
                overview_df.at[outer_index,
                               f'Review: {num_scores_for_user}'] = score

    overview_df = overview_df.drop(['SID'], axis=1)

    return overview_df


def _user_lookup(key, users):
    """Given a user id and a list of users, search list for user with
       matching id. If found, return user name, else return string 'Not Found'

    Args:
        key (str): User id to match on
        users (list of obj): List of users objects (students)

    Return:
        (str): User name if found, 'Not Found' otherwise
    """
    for user in users:
        if key == user.id:
            return user.name

    return 'Not Found'


def _expand_criteria_to_columns(assessments_df, list_of_rubric_criteria):
    """Expands the 'data' column in the assessments_df DataFrame. Makes column
       for each criteria in the rubric, titles it by description and score and
       puts assessment points under their respective criteria column.

       ASSESSMENTS (BEFORE):
         assessor_id | artifact_id | data                 | score
         2907        | 198867      | {'id': None,         | 35
                                      'points': 12.0, 
                                      'criterion_id': 
                                      'description':
                                      "Quality of Writing"
                                      ...

        ASSESSMENTS (AFTER):
        assessor_id | artifact_id | score | Quality of Writing (25) | ...
        2907        | 198867      | 35    | 12                      | ...


    Args:
        assessments_df (DataFrame): Completed assessments with points breakdown
                                    in 'data' column
        list_of_ribric_criteria (JSON): List of criteria objects from rubric

    Returns:
        assessments_df (DataFrame): DataFrame as described above.
    """

    # For each row, step through row['data'] object. For every criteria,
    # take the points that have been awarded and put into column with that
    # criterion id (expanding that data cell into separate columns)
    for index, row in assessments_df.iterrows():
        for item in row['data']:
            value = None
            if not math.isnan(item['points']):
                value = item['points']
            col = item['criterion_id']
            assessments_df.at[index, col] = value

    # Make object matching criterion id (keys) to more descriptive column names
    # EX.
    # {'_1220': 'Quality of Writing (25.0)',
    #  '_1409': 'Quality of Critique (25.0)',
    #  '_3869': 'Grammer, Usage and Mechanics (15.0)'}
    new_names = {}
    for crit in list_of_rubric_criteria:
        crit_id = crit['id']
        crit_description = crit['description']
        crit_points = crit['points']
        new_names[crit_id] = f"{crit_description} ({crit_points})"

    # assign new names to criteria columns
    assessments_df = assessments_df.rename(columns=new_names)

    # delete original data column
    del assessments_df['data']

    return assessments_df


def _make_students_df(paginated_list_of_students):
    """Given a paginated list of canvasapi objects, iterate through each item,
       take the JSON used to create that object and append to an output list.
       Finally, convert that list to a DataFrame and return.

    Args:
        paginated_list_of_student (paginated list of type User -- canvasapi): List of User objects

    Returns:
        students_df (DataFrame): table containing each student in given course
    """
    students = []
    for student in paginated_list_of_students:
        students.append(student.attributes)

    students_df = pd.DataFrame(students)
    return students_df


def _make_assigned_completed_df(students_df, peer_reviews_df):
    """Creates a table with one row per student. Columns for Canvas ID, name, sid,
       number of assigned peer reviews and number of completed peer reviews.

    Args:
        students_df (DataFrame): Students table
        peer_reviews_df (DataFrame): Peer reviews table

    Returns:
        df (DataFrame): Table with one row per student num assigned num
        completed columns

    """
    pruned_df = students_df[['id', 'name', 'sis_user_id']]

    df = pruned_df.rename(
        columns={'id': 'CanvasUserID',
                 'name': 'Name',
                 'sis_user_id': 'SID'})

    df.insert(3, 'Num Assigned Peer Reviews', None)
    df.insert(4, 'Num Completed Peer Reviews', None)

    for index, row in df.iterrows():
        lookup = _lookup_reviews(row['CanvasUserID'], peer_reviews_df)
        df.at[index, 'Num Assigned Peer Reviews'] = lookup['Assigned']
        df.at[index, 'Num Completed Peer Reviews'] = lookup['Completed']

    return df


def _lookup_reviews(uid, peer_reviews):
    """Given a user id (uid), finds number of assigned and completed peer reviews
       for that given student in the peer_reviews table. Returns dictionary with
       'Assigned' and 'Completed' counts.

    Args:
        uid (int): User id to search for
        peer_reviews (DataFrame): Peer reviews table

    Returns:
        Dictionary with two keys, 'Assigned' and 'Completed' with
        number of assigned/completed peer reviews as values

    """
    assigned_subset = peer_reviews[peer_reviews['assessor_id'] == uid]
    completed_subset = assigned_subset[assigned_subset['workflow_state'] == 'completed']

    assigned = len(assigned_subset)
    completed = len(completed_subset)

    return {
        'Assigned': assigned,
        'Completed': completed
    }
