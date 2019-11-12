from pick import pick
import pandas as pd
import pprint
import time
import os
import getpass
import sys

CANVAS_INSTANCES = ['https://canvas.ubc.ca',
                    'https://ubc.instructure.com',
                    'https://ubc.test.instructure.com',
                    'https://ubcsandbox.instructure.com']


def get_user_inputs():
    # ENTER THE FOLLOWING INFORMATION
    token = getpass.getpass('Enter your token: ')

    # course url
    url = pick(CANVAS_INSTANCES,
               'Select the canvas instance to use.')[0]

    # course number
    course = input('course number: ')

    # the assignment ID number
    assignment_id = input('assignment_id: ')

    return {
        'token': token,
        'url': url,
        'course': course,
        'assignment_id': assignment_id
    }


def make_assessment_df(assessments):
    if not assessments:
        shut_down(
            'Error: there must be at least one completed assessment for the given rubric.')

    for value in assessments:
        to_delete = value['rubric_association']
        del to_delete['summary_data']

    return pd.DataFrame(assessments)


def make_peer_review_df(peer_review):
    df = pd.DataFrame(peer_review)
    # df['user_id'] = df['user_id'].astype(str)

    return df


def make_output_tables(df1, df2, users_df, course, max_points):
    """
    OUTDATED!!!
    merge the peerReview_df and the assessments_df by the assessor_id and asset_id
    in assessments df the assessor_id and artifact_id
    in the peer review df the assessor_id and asset_id
    write merged dataframe to csv
    """

    now = time.strftime("%c")

    merged_df = pd.merge(df1, df2,
                         how='left',
                         left_on=['assessor_id', 'asset_id'],
                         right_on=['assessor_id', 'artifact_id'])

    merged_df = pd.merge(merged_df, users_df[['id', 'name']],
                         how='left',
                         left_on='assessor_id',
                         right_on='id',
                         suffixes=('', '_assessor'))

    merged_df = pd.merge(merged_df, users_df[['id', 'name']],
                         how='left',
                         left_on='user_id',
                         right_on='id',
                         suffixes=('', '_assessee'))

    merged_df = merged_df.rename(columns={'id_x': 'EvalID', 'assessor_id': 'AssessorID', 'name': 'Assessor Name',
                                          'user_id': 'AssesseeID', 'name_assessee': 'Assessee Name', 'rubric_id': 'RubricID',
                                          'score': 'Score', 'data': 'Score by Rubric Item'})

    # print(merged_df['Score by Rubric Item'])
    # exit()
    only_completed_df = merged_df[merged_df['RubricID'] > 0]
    item_table = make_item_table(
        only_completed_df[['EvalID', 'Score by Rubric Item']])

    user_table = make_user_table(users_df, df1)

    pruned = merged_df[['AssessorID', 'Assessor Name',
                        'AssesseeID', 'Assessee Name',
                        'RubricID', 'Score', 'EvalID']]

    pruned.insert(6, 'Max Possible Score', max_points)

    all_dfs_merged = pd.merge(user_table, pruned,
                              how='right',
                              left_on='CanvasUserID',
                              right_on='AssessorID')

    all_dfs_merged = pd.merge(all_dfs_merged, item_table,
                              how='left',
                              left_on='EvalID',
                              right_on='EvalID')

    dir_name = f'{course}-{now}'

    os.mkdir(f'data/{dir_name}')

    pruned.to_csv(
        f'data/{dir_name}/peer_reviews.csv', index=False)

    item_table.to_csv(f'data/{dir_name}/items.csv', index=False)

    user_table.to_csv(f'data/{dir_name}/users.csv', index=False)

    all_dfs_merged.to_csv(f'data/{dir_name}/merged.csv', index=False)


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
    # print(peer_reviews)
    # exit()
    assigned_subset = peer_reviews[peer_reviews['assessor_id'] == uid]
    completed_subset = assigned_subset[assigned_subset['workflow_state'] == 'completed']

    assigned = len(assigned_subset)
    completed = len(completed_subset)

    return {
        'Assigned': assigned,
        'Completed': completed
    }


def make_item_table(reviews_df):
    pd.options.mode.chained_assignment = None  # default='warn'
    # print(len(completed_reviews_df[0]['Score by Rubric Item']))
    for index, row in reviews_df.iterrows():

        item_num = 1
        for item in row['Score by Rubric Item']:
            value = item['points']
            col = 'Item ' + str(item_num)
            reviews_df.at[index, col] = value
            # reviews_df.at[index, 'Item ' + str(item_num)] = item['points']
            # print(str(index) + ' ' + str(item_num) + ": " + str(item['points']))
            item_num += 1

    del reviews_df['Score by Rubric Item']

    return reviews_df


def shut_down(msg):
    """Shuts down the script

    Args:
        msg (string): message to print before printing 'Shutting down...' and exiting the script
    """
    print(msg)
    print('Shutting down...')
    sys.exit()
