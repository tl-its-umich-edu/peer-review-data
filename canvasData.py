# -*- coding: utf-8 -*-
from logging import Logger, getLogger
from typing import List

from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.rubric import Rubric
from canvasapi.submission import Submission
from canvasapi.user import User

import config

LOGGER: Logger = getLogger(__name__)

canvas = Canvas(config.CANVAS_BASE_URL, config.CANVAS_API_TOKEN)


class CanvasUser(User):
    id: int
    name: str
    sortable_name: str
    login_id: str


class CanvasCourse(Course):
    id: int
    name: str
    course_code: str


class CanvasAssignment(Assignment):
    id: int
    name: str
    course_id: int
    peer_reviews: bool
    rubric_settings: dict


class CanvasComment(object):
    def __init__(self, comment: dict):
        self.__comment = comment

    @property
    def criterionId(self) -> int:
        return int(self.__comment['criterion_id'][1:])

    @property
    def comments(self) -> str:
        return self.__comment['comments']


class CanvasAssessment(object):
    def __init__(self, assessment: dict):
        self.__assessment = assessment

    @property
    def id(self) -> int:
        return self.__assessment['id']

    @property
    def assessorId(self) -> int:
        return self.__assessment['assessor_id']

    @property
    def isPeerReview(self) -> bool:
        return self.__assessment['assessment_type'] == 'peer_review'

    @property
    def hasSubmission(self) -> bool:
        return self.__assessment['artifact_type'] == 'Submission'

    @property
    def submissionId(self) -> int:
        return self.__assessment['artifact_id'] if self.hasSubmission else None

    @property
    def comments(self) -> List[CanvasComment]:
        return self.__assessment['data']

    data: List[dict]


class CanvasCriteria(object):
    def __init__(self, criteria: dict):
        self.__criteria = criteria

    @property
    def id(self) -> int:
        """
        Canvas' RubricCriterion objects contain ID *strings* of the format
        `"_nnn…"`.  It's not clear from the docs *why* they are that format.
        Here, we assume that the ID will be unique if everything following the
        underscore is converted to an integer.

        :return: RubricCriterion ID, stripped and converted to an integer.
        """
        return int(self.__criteria['id'][1:])

    @property
    def description(self) -> str:
        return self.__criteria['description']

    @property
    def longDescription(self) -> str:
        return self.__criteria['long_description']

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'"{self.description}"; "{self.longDescription}"'


class CanvasRubric(Rubric):
    id: int
    title: str
    course_id: int

    __criteria: List[CanvasCriteria] = None
    data: List[dict]

    def __init__(self, rubric: dict):
        self.__rubric = rubric

    @property
    def criteria(self) -> List[CanvasCriteria]:
        if self.__criteria is None:
            d = self.__dict__
            self.__criteria = [CanvasCriteria(c) for c in
                               d.get('criteria', d.get('data'))]
        return self.__criteria

    assessments: List[CanvasAssessment]


class CanvasSubmission(Submission):
    id: int
    assignment_id: int
    user_id: int
    submission_type: str
