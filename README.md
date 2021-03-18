# Canvas Peer Reviews

> - name: canvas-peer-reviews
> - ops-run-with: jupyter
> - python>=3.7
> - canvasapi>=2.0.0
> - supports universal environment 🌎

## Summary

__Canvas Peer Reviews__ is a Jupyter Notebook and Python script that works with Canvas LMS Data to create formatted .csv tables containing peer review data. Upon providing the necessary inputs, the script will produce two .csv files in the "peer_review_data" folder (in the project's root directory). The data tables will provide an overview of all assigned peer reviews for a given assignment - including all students who've been assigned as assessors, who they are assessing and the results of any completed assessments. When executed, the notebook/script will also prompt about a optional third .csv containing non-peer-reviewed scores for the given assignment.

> :warning: There is no equivalent functionality in the Canvas interface for easily accessing this data. Peer Reviews in Canvas can be odd, and the rubric behaviour is not always intuitive for students. Instructors should review the peer review data provided before making any grading decisions, in particular any cases where a review has a score of 0, or the scores seem inconsistent. Where inconsistencies exist in the data, we recommend reviewing in the Canvas interface.

---

## Inputs

- Base URL _(Instance of Canvas being used - ex. https://ubc.instructure.com)_
- Canvas Token _(generate through Account => Settings)_
- Course ID _(last digits of URL when visiting course page)_
- Assignment ID _(last digits of URL when visiting assignment page)_
- To include the assignment scores if graded in addition to peer reviewed (generates additional csv) _(y/n)_

## Output

### peer_review_assessments.csv:

_Lists all assigned assessments including roles of assessee/assessor, total score and score given for each rubric item (Note: all columns pertaining to score will be blank if a review is not completed yet)._

- **State:** State of the peer review (completed, assigned etc.)
- **Assessee:** Name of the student who's work is being evaluated.
- **Assessor:** Name of the student who is evaluating the assessee.
- **Total Score (`points_possible`):** The total score given by the assessor to the assessee, where `points possible` is the maximum possible score for the assignment.
- **`criteria_description` (`criteria_points`):** The score breakdown per criteria item as they appear in the rubric. Will be as many columns as criteria items in rubric **(1...n)**. `criteria_description` will be the the heading of a single rubric item and `criteria_points` is the maximum possible score for that item.

### peer_review_overview.csv:

_Lists each student in the course by canvas user id and name, shows # of assigned peer reviews as well as # of completed reviews; for each student, if that student has been evaluated, their scores will appear in the "Review" columns._

- **CanvasUserID:** The user id of the student as it appears on Canvas.
- **Name:** The student's name
- **Num Assigned Peer Reviews:** The number of peer reviews that have been assigned to the student.
- **Num Completed Peer Reviews:** The number of peer reviews that have been completed by the student.
- **Review: `review_number`:** The score the student has been awarded from a single peer review (blank if review is not complete). Will be as many columns as there are completed peer reviews for a particular student **(1...n)** `review_number` will count up from 1 to help identify one review from another.

### peer_review_given_score.csv
_(optional) Lists each student in the course by canvas user id, shows the non-peer-review given score (if graded in addition to peer reviewed). This is an optional output._

- **CanvasUserID:** The user id of the student as it appears on Canvas.
- **Score:** The total score given for an assignment (by a "grader"). 
- **GradingWorkflowState:** Details about the grading workflow state. 
## Getting Started
### Sauder Operations

_Are you Sauder Operations Staff? Please go [here](https://github.com/saud-learning-services/instructions-and-other-templates/blob/main/docs/running-instructions.md) for detailed instructions to run in Jupyter. ("The Project", or "the-project" is "canvas-peer-reviews" or "Canvas Peer Reviews")._

### General (terminal instructions)

> Project uses **conda** to manage environment (See official **conda** documentation [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file))

#### First Time

1. Ensure you have [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) installed (Python 3.7 version)
1. Clone **canvas-peer-reviews** repository
1. Import environment (once): `$ conda env create -f environment.yml`

#### Every Time

1. Run
   1. `$ conda activate canvas-peer-reviews`
   1. `python src/peer_review.py`
   1. Follow terminal prompts

---

_authors: @markoprodanovic @alisonmyers_
