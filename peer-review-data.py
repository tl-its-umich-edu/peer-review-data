# -*- coding: utf-8 -*-
import json
import os

from canvasapi import Canvas
from canvasapi.assignment import Assignment

CANVAS_API_URL: str = os.getenv('CANVAS_API_URL',
                                'https://canvas-test.it.umich.edu/')
CANVAS_API_TOKEN: str = os.getenv('CANVAS_API_TOKEN')
COURSE_ID: str = os.getenv('COURSE_ID')
ASSIGNMENT_ID: str = os.getenv('ASSIGNMENT_ID')

if CANVAS_API_TOKEN is None:
    raise RuntimeError('"CANVAS_API_TOKEN" was not set.')

canvas = Canvas(CANVAS_API_URL, CANVAS_API_TOKEN)


class CanvasAssignment(Assignment):
    id: int
    description: str
    peer_reviews: bool
    automatic_peer_reviews: bool
    anonymous_peer_reviews: bool
    rubric_settings: dict


course = canvas.get_course(COURSE_ID)
assignment: CanvasAssignment = course.get_assignment(ASSIGNMENT_ID)

# print(repr(assignment))
# print(assignment.description)
# print(assignment.id)
# print(assignment.peer_reviews)
# print(assignment.rubric_settings)

notPeerReviews = assignment.get_peer_reviews(include=['submission_comments', 'user'], per_page=100)

# review comments are from instructor/TA, NOT the reviewer
print(repr(list(notPeerReviews)))

# https://canvas-test.it.umich.edu/api/v1/courses/545451/rubrics/120238?include[]=peer_assessments&style=full
# peerReviews = course.get_rubric(120238, include='peer_assessments',
#                                 style='full')
# print(repr(peerReviews))
# print(repr(peerReviews.assessments))
# json.dump(peerReviews.assessments, open('assessments.json', 'w'), indent=2)
