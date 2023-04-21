# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List

from canvasapi.course import Course
from canvasapi.rubric import Rubric
from django.utils.timezone import utc

import config
from canvasData import (
    canvas,
    CanvasAssessment,
    CanvasAssignment,
    CanvasCourse,
    CanvasComment,
    CanvasCriteria,
    CanvasRubric,
    CanvasSubmission
)
from peer_review_data import models
from utils import dictSkipKeys

LOGGER = logging.getLogger(__name__)


def saveCourseAndUsers(canvasCourse: CanvasCourse) -> models.Course:
    course = models.Course.fromCanvasCourse(canvasCourse)
    LOGGER.debug(f'Saving {course}…')
    course.save()

    LOGGER.debug(f'Saving users of {course}…')
    '''
    Possible bug in `canvasapi` module…
    When calling `get_users` with the argument `include='test_student'`, the
    module adds it to the URL as `include=test_studentanalytics_url`.  The
    origin of the "analytics_url" string is unknown.  However, it's known that
    the Canvas API expects the "include" argument to appear as `include[]`, so
    by using a dictionary here with the key in the correct format, the bug is
    bypassed and the argument appears correctly.
    Strangely, a later call to `get_rubric` uses the `include` keyword argument
    without problem.
    '''
    for canvasUser in canvasCourse.get_users(**{'include[]': 'test_student'}):
        try:
            user = models.User.fromCanvasUser(canvasUser)
            LOGGER.debug(f'Saving {user}…')
            user.save()
        except Exception as e:
            LOGGER.warning(f'Error saving {user}: {e}')

    return course


def saveSubmissions(canvasAssignment: CanvasAssignment):
    canvasSubmissions: List[CanvasSubmission] = \
        canvasAssignment.get_submissions()

    for canvasSubmission in canvasSubmissions:
        try:
            submission: models.Submission = \
                models.Submission.fromCanvasSubmission(canvasSubmission)
            LOGGER.debug(f'Saving {submission}…')
            submission.save()
        except Exception as e:
            LOGGER.warning(f'Error saving Submission: {e}')
            LOGGER.debug(json.dumps(
                dictSkipKeys(canvasSubmission, ['_requester']),
                indent=2, default=str))


def saveRubricAndCriteria(canvasRubric: CanvasRubric,
                          canvasAssignment: CanvasAssignment):
    rubric = models.Rubric.fromCanvasRubricAndAssignment(canvasRubric,
                                                         canvasAssignment)
    LOGGER.debug(f'Saving {rubric}…')
    rubric.save()

    criteria: Dict[int, models.Criterion] = {}

    '''
    Rubric objects always contain criteria in the `data` property, and also
    in the `criteria` property when assessments are requested.  Use `data`
    to ensure access to the criteria.
    '''
    for canvasCriterion in canvasRubric.data:
        criterion = models.Criterion.fromCanvasCriterionAndRubric(
            CanvasCriteria(canvasCriterion), rubric)
        LOGGER.debug(f'Saving {criterion}…')
        criterion.save()
        criteria[criterion.id] = criterion

    return rubric, criteria


def saveAssessmentsAndComments(
        canvasAssessments: List[CanvasAssessment]) -> None:
    """
    Given a list of `CanvasAssessment` objects, save those that are
    peer reviews.  When saving assessments, save their
    comments with the appropriate model.

    :param canvasAssessments:
    :return: None
    """
    canvasAssessment: CanvasAssessment
    for canvasAssessment in [CanvasAssessment(a) for a in
                             canvasAssessments]:
        if not canvasAssessment.isPeerReview:
            LOGGER.warning(f'Assessment ({canvasAssessment.id}) '
                           'is NOT a peer-review.')

        assessment: Optional[models.Assessment] = None
        try:
            assessment = \
                models.Assessment.fromCanvasAssessment(canvasAssessment)

            if assessment is None:
                continue

            LOGGER.debug(f'Saving {assessment}…')
            assessment.save()
        except Exception as e:
            # XXX: Catch assessment referring to missing assessor or submission
            LOGGER.warning(f'Error saving Assessment ({canvasAssessment.id}; '
                           f'Submission: {canvasAssessment.submissionId}; '
                           f'Assessor: {canvasAssessment.assessorId}): {e}')
            LOGGER.debug('Assessment data: ' + json.dumps(
                dictSkipKeys(canvasAssessment, ['_requester']),
                indent=2, default=str))
            continue

        canvasComment: CanvasComment
        for canvasComment in [CanvasComment(c) for c in
                              canvasAssessment.comments]:
            try:
                comment: models.Comment = \
                    models.Comment.fromCanvasCommentAndAssessment(
                        canvasComment, assessment)
                LOGGER.debug(f'Saving {comment}…')
                comment.save()
            except Exception as e:
                LOGGER.warning(f'Error saving {comment}: {e}')


def processCourseAssignments(canvasCourse: CanvasCourse):
        courseSaved = False

        canvasAssignments: List[CanvasAssignment] = \
            canvasCourse.get_assignments()

        canvasAssignment: CanvasAssignment
        # Iterate over assignments which have peer reviews
        for canvasAssignment in filter(
            lambda a: a.peer_reviews is True, canvasAssignments):
        LOGGER.debug(f'Found peer reviewed assignment '
                     f'({canvasAssignment.id}): '
                f'"{canvasAssignment.name}"')

            assignmentRubricId: int = canvasAssignment.rubric_settings.get(
                'id')
            LOGGER.debug(f'Assignment ({canvasAssignment.id}) has '
                         f'rubric ID ({assignmentRubricId})')

            canvasAssignmentRubric: CanvasRubric = canvasCourse.get_rubric(
                assignmentRubricId, include='assessments', style='full')

            if not hasattr(canvasAssignmentRubric, 'assessments'):
            LOGGER.debug(f'Skipping assignment ({canvasAssignment.id}) in '
                         f'course ({canvasCourse.id}): Not configured '
                         f'for peer reviews ("assessments").')
                continue

        LOGGER.debug(f'Assignment ({canvasAssignment.id}) '
                     f'in course ({canvasCourse.id}) is '
                        'configured for peer reviews ("assessments")…')

            if len(canvasAssignmentRubric.assessments) == 0:
            LOGGER.debug(
                    f'Skipping assignment ({canvasAssignment.id}) '
                f'in course ({canvasCourse.id}): '
                    'No peer reviews ("assessments") were found.')
                continue

            LOGGER.info(f'Assignment ({canvasAssignment.id}) '
                    f'in course ({canvasCourse.id}) has '
                        'peer reviews ("assessments")…')

        course: Optional[models.Course] = None
            if not courseSaved:
                course = saveCourseAndUsers(canvasCourse)
                if course:
                    courseSaved = True
                else:
                    LOGGER.error(f'Course ({canvasCourse.id}) '
                                 'and its users were not saved.')
                    continue

            assignment: models.Assignment = \
                models.Assignment.fromCanvasAssignment(canvasAssignment)
        LOGGER.debug(f'Saving {assignment}…')
            assignment.save()

        LOGGER.debug(f'Saving submissions for {assignment}…')
            saveSubmissions(canvasAssignment)

        LOGGER.debug(f'Saving rubric and criteria for {assignment}…')
        saveRubricAndCriteria(canvasAssignmentRubric, canvasAssignment)

        LOGGER.debug(f'Saving assessments and comments for {assignment}…')
            saveAssessmentsAndComments(canvasAssignmentRubric.assessments)


def main() -> None:
    timeStart: datetime = datetime.now(tz=utc)
    LOGGER.info(f'Start time: {timeStart.isoformat(timespec="milliseconds")}')

    courseId: str
    for courseId in config.COURSE_IDS:
        canvasCourse: CanvasCourse = canvas.get_course(courseId)
        LOGGER.info(f'Checking course ({canvasCourse.id}): '
                    f'"{canvasCourse.name}"…')
        processCourseAssignments(canvasCourse)

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
