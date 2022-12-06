# -*- coding: utf-8 -*-
import os

from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.rubric import Rubric

CANVAS_API_URL: str = os.getenv('CANVAS_API_URL',
                                'https://canvas-test.it.umich.edu/')
CANVAS_API_TOKEN: str = os.getenv('CANVAS_API_TOKEN')
COURSE_ID: str = os.getenv('COURSE_ID')
ASSIGNMENT_ID: str = os.getenv('ASSIGNMENT_ID')

if CANVAS_API_TOKEN is None:
    raise RuntimeError('"CANVAS_API_TOKEN" was not set.')

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


class CanvasRubric(Rubric):
    assessments: dict
