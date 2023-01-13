# -*- coding: utf-8 -*-
import os
import sys
from logging import Logger, getLogger
from typing import List

from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.rubric import Rubric

LOGGER: Logger = getLogger(__name__)

CANVAS_API_URL: str = os.getenv('CANVAS_API_URL',
                                'https://canvas-test.it.umich.edu/')
CANVAS_API_TOKEN: str = os.getenv('CANVAS_API_TOKEN')
COURSE_ID: str = os.getenv('COURSE_ID')
ASSIGNMENT_ID: str = os.getenv('ASSIGNMENT_ID')

envErrors = []

if CANVAS_API_TOKEN is None:
    envErrors.append('CANVAS_API_TOKEN')

if COURSE_ID is None:
    envErrors.append('COURSE_ID')

if ASSIGNMENT_ID is None:
    envErrors.append('ASSIGNMENT_ID')

if len(envErrors) > 0:
    LOGGER.critical('The following environment variable(s) are not set: '
                    f'{", ".join(envErrors)}')
    sys.exit()

canvas = Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)


class CanvasCourse(Course):
    id: int
    name: str


class CanvasAssignment(Assignment):
    id: int
    name: str
    description: str
    peer_reviews: bool
    rubric_settings: dict


class CanvasAssessmentComment(object):
    pass


class CanvasAssessment(object):
    def __init__(self, assessment: dict):
        self.__assessment = assessment

    @property
    def id(self) -> int:
        return self.__assessment['id']

    @property
    def assessorId(self) -> int:
        return self.__assessment['assessor_id']

    data: List[dict]


class CanvasRubric(Rubric):
    criteria: List[dict]
    assessments: List[CanvasAssessment]
