"""
PEER REVIEW SCRIPT: settings

This file is responsible for defining/initializing global variables.

authors:
@markoprodanovic

last edit:
Monday, January 10, 2020
"""
from canvasapi import canvas


def init():

    # Canvas object to provide access to Canvas API
    global course

    # Assignment object representing Canvas assignment specified by user input
    global assignment
