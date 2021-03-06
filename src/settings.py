"""
PEER REVIEW SCRIPT: settings

This file is responsible for defining/initializing global variables.

authors:
@markoprodanovic

last edit:
Monday, April 26, 2021
"""

import os


# Project ROOT directory
ROOT = os.path.dirname(os.path.abspath(__file__))

# Canvas object to provide access to Canvas API
COURSE = None

# Assignment object representing Canvas assignment specified by user input
ASSIGNMENT = None

# Whether to include output of assignment scored (specified by user input)
INCLUDE_ASSIGNMENT_SCORE = None
