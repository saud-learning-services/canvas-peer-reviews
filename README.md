# Peer Review Info

### Summary
*Peer Review Info* is a Jupyter Notebook and Python script that works with Canvas LMS Data to create formatted .csv tables containing Canvas peer review data. Upon providing the necessary inputs, the notebook will produce two .csv files in the "peer_review_data" folder (in project root directory). The data tables will give users an overview all assigned peer reviews for a given assignment - including all students who've been assigned as assessors, who they are assessing and the results of any completed assessments.

---

### Input
* Base URL *(Instance of Canvas being used - ex. canvas.ubc.ca)*
* Canvas Token *(generate through Account => Settings)*
* Course ID *(last digits of URL when visiting course page)*
* Assignment ID *(last digits of URL when visiting assignment page)*

### Output
* **peer_review_assessments.csv:** Lists all assigned assessments including roles of assessee/assessor, total score and score given for each rubric item (Note: all columns pertaining to score will be blank if a review is not completed yet)

* **peer_review_overview.csv:** Lists each student in the course by canvas user id and name, shows # of assigned peer reviews as well as # of completed reviews; for each student, if that student has been evaluated, their scores will appear in the "Review" columns.

---

*authors: @markoprodanovic @alisonmyers*