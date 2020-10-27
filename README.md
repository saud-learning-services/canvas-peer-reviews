# Peer Review Info

## Summary
*Peer Review Info* is a Jupyter Notebook and Python script that works with Canvas LMS Data to create formatted .csv tables containing Canvas peer review data. Upon providing the necessary inputs, the notebook will produce two .csv files in the "peer_review_data" folder (in project root directory). The data tables will give users an overview all assigned peer reviews for a given assignment - including all students who've been assigned as assessors, who they are assessing and the results of any completed assessments.

> :warning: There is no equivalent functionality in the Canvas interface for easily accessing this data. Peer Reviews in Canvas can be odd, and the rubric behaviour is not always intuitive for students. Instructors should review the peer review data provided before making any grading decisions, in particular any cases where a review has a score of 0.  

---

## Input
* Base URL *(Instance of Canvas being used - ex. canvas.ubc.ca)*
* Canvas Token *(generate through Account => Settings)*
* Course ID *(last digits of URL when visiting course page)*
* Assignment ID *(last digits of URL when visiting assignment page)*

## Output

### peer_review_assessments.csv:
*Lists all assigned assessments including roles of assessee/assessor, total score and score given for each rubric item (Note: all columns pertaining to score will be blank if a review is not completed yet).*


* **Assessee:** Name of the student who's work is being evaluated.
* **Assessor:** Name of the student who is evaluating the assessee.
* **Total Score (```points_possible```):** The total score given by the assessor to the assessee, where ```points possible``` is the maximum possible score for the assignment.
* **```criteria_description``` (```criteria_points```):** The score breakdown per criteria item as they appear in the rubric. Will be as many columns as criteria items in rubric **(1...n)**. ```criteria_description``` will be the the heading of a single rubric item and ```criteria_points``` is the maximum possible score for that item.
    
    
### peer_review_overview.csv:
*Lists each student in the course by canvas user id and name, shows # of assigned peer reviews as well as # of completed reviews; for each student, if that student has been evaluated, their scores will appear in the "Review" columns.*

* **Canvas User ID:** The user id of the student as it appears on Canvas.
* **Name:** The student's name
* **Num Assigned Peer Reviews:** The number of peer reviews that have been assigned to the student.
* **Num Completed Peer Reviews:** The number of peer reviews that have been completed by the student.
* **Review: ```review_number```:** The score the student has been awarded from a single peer review (blank if review is not complete). Will be as many columns as there are completed peer reviews for a particular student **(1...n)** ```review_number``` will count up from 1 to help identify one review from another.

---

*authors: @markoprodanovic @alisonmyers*
