# Peer Review Info

### Summary
*Peer Review Info* is a Jupyter Notebook and Python script that works with Canvas LMS Data to create formatted .csv tables containing Canvas peer review data. Upon providing the necessary inputs, the notebook will produce three .csv files in /data in the project root directory. The data tables will give users an overview all assigned peer reviews for a given assignment - including all students who've been assigned as assessors, who they are assessing and the results of any completed assessments.

---

### Input
* Canvas token *(generate through Account => Settings)*
* Course ID *(last digits of URL when visiting course page)*
* Assignment ID *(last digits of URL when visiting assignment page)*

### Output
* **users.csv:**  Complete list of users in specified course and number of assigned/completed peer reviews
* **peer_reviews.csv:**  Specifies assessor/assessee pairings and scores (for completed assessments)
* **items.csv:**  Completed assessments indentified by a unique id and scores for each item in rubric

---

*authors: @alisonmyers @markoprodanovic*