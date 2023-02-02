# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from typing import Dict

from django.utils.timezone import utc

from canvasData import *
from peer_review_data import models
from utils import dictSkipKeys

LOGGER: Logger = getLogger(__name__)


def saveCourseAndUsers(canvasCourse: CanvasCourse) -> (bool, Course):
    course = models.Course.fromCanvasCourse(canvasCourse)
    LOGGER.info(f'Saving {course}…')
    course.save()

    # FIXME: DEBUG - uncomment for finished product
    # for canvasUser in canvasCourse.get_users():
    #     u = models.User.fromCanvasUser(canvasUser)
    #     LOGGER.info(f'Saving {u}…')
    #     u.save()

    return True, course


def saveSubmissions(canvasAssignment: CanvasAssignment):
    canvasSubmissions: List[CanvasSubmission] = \
        canvasAssignment.get_submissions()

    for canvasSubmission in canvasSubmissions:
        '''
        The only untyped submission found during development was from 
        "Test Student".  It was discovered because that student wasn't
        included with the rest of the course users and the relationship to
        the user couldn't be created.  Testing for untyped submissions
        will eliminate those from "Test Student" and possibly others.
        '''
        if canvasSubmission.submission_type is None:
            LOGGER.warning('Skipping untyped submission '
                           f'({canvasSubmission.id}) for '
                           f'user ID ({canvasSubmission.user_id}).')
            continue

        try:
            submission: models.Submission = \
                models.Submission.fromCanvasSubmission(canvasSubmission)
            LOGGER.info(f'Saving {submission}…')
            submission.save()
        except Exception as e:
            LOGGER.warning(f'Exception while saving Submission: {e}')
            LOGGER.warning(json.dumps(
                dictSkipKeys(canvasSubmission, ['_requester']),
                indent=2, default=str))


def saveRubricAndCriteria(canvasRubric: CanvasRubric,
                          canvasAssignment: CanvasAssignment
                          ) -> [Rubric, Dict[int, models.Criterion]]:
    rubric = models.Rubric.fromCanvasRubricAndAssignment(canvasRubric,
                                                         canvasAssignment)
    LOGGER.info(f'Saving {rubric}…')
    rubric.save()

    criteria: Dict[int, models.Criterion] = {}

    # Get criteria from canvasRubric.data
    for canvasCriterion in canvasRubric.data:
        criterion, created = models.Criterion.fromCanvasCriterionAndRubric(
            CanvasCriteria(canvasCriterion), rubric)
        if criterion:
            if created:
                LOGGER.info(f'Created {criterion}…')
            criteria[criterion.id] = criterion

    return rubric, criteria


def saveAssessmentsAndComments(canvasAssessments: List[CanvasAssessment]):
    # FIXME: Debugging with first assessment only.  Expand to all assessments.
    # assessment: CanvasAssessment = CanvasAssessment(
    #     canvasAssignmentRubric.assessments[0])
    # LOGGER.info(f'**** Assessment 0 --> ID: ({assessment.id}), '
    #             f'assessor ID: ({assessment.assessorId})')

    canvasAssessment: CanvasAssessment
    for canvasAssessment in [CanvasAssessment(a) for a in
                             canvasAssessments]:
        if not canvasAssessment.isPeerReview:
            LOGGER.info('Skipping non-peer-review assessment '
                        f'({canvasAssessment.id}).')
            continue

        assessment: models.Assessment = None
        try:
            assessment = \
                models.Assessment.fromCanvasAssessment(canvasAssessment)
            LOGGER.info(f'Saving {assessment}…')
            assessment.save()
        except Exception as e:
            # XXX: Catches assessments referring to non-existent submissions!
            LOGGER.warning(f'Exception while saving Assessment '
                           f'({canvasAssessment.id}): {e}')
            LOGGER.warning(json.dumps(
                dictSkipKeys(canvasAssessment, ['_requester']),
                indent=2, default=str))

        if assessment:
            canvasComment: CanvasComment
            for canvasComment in [CanvasComment(c) for c in
                                  canvasAssessment.comments]:
                comment: models.Comment = \
                    models.Comment.fromCanvasCommentAndAssessment(
                        canvasComment, assessment)
                LOGGER.info(f'Saving {comment}…')
                comment.save()


def main() -> None:
    timeStart: datetime = datetime.now(tz=utc)
    LOGGER.info(f'Start time: {timeStart.isoformat(timespec="milliseconds")}')

    canvasCourse: CanvasCourse = canvas.get_course(COURSE_ID)
    LOGGER.info(f'Found course ({canvasCourse.id}): "{canvasCourse.name}"')
    courseSaved = False
    course: models.Course | None = None
    user: models.User | None = None

    # LOGGER.info(dictSkipKeys(canvasCourse, ['_requester']))
    # sys.exit()

    canvasAssignment: CanvasAssignment = canvasCourse.get_assignment(
        ASSIGNMENT_ID)
    LOGGER.info(
        f'Found assignment ({canvasAssignment.id}): "{canvasAssignment.name}"')

    if canvasAssignment.peer_reviews is not True:
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'Not configured for peer reviews.')
        sys.exit()

    LOGGER.info(f'Assignment ({canvasAssignment.id}) is peer reviewed')

    assignmentRubricId: int = canvasAssignment.rubric_settings.get('id')
    LOGGER.info(f'Assignment ({canvasAssignment.id}) has '
                f'rubric ID ({assignmentRubricId})')

    outputFileName: str = 'rubric.json'
    canvasAssignmentRubric: CanvasRubric = canvasCourse.get_rubric(
        assignmentRubricId, include='assessments', style='full')

    if not hasattr(canvasAssignmentRubric, 'assessments'):
        LOGGER.info(f'Skipping assignment ({ASSIGNMENT_ID}) in '
                    f'course ({COURSE_ID}): Not configured for peer reviews '
                    '("assessments").')
        sys.exit()

    LOGGER.info(f'Assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}) is '
                'configured for peer reviews ("assessments")…')

    if not hasattr(canvasAssignmentRubric, 'assessments'):
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'No peer reviews ("assessments") were found.')
        sys.exit()

    LOGGER.info(f'Assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}) has '
                'peer reviews ("assessments")…')

    if not courseSaved:
        courseSaved, course = saveCourseAndUsers(canvasCourse)

    assignment: models.Assignment = models.Assignment.fromCanvasAssignment(
        canvasAssignment)
    LOGGER.info(f'Saving {assignment}…')
    assignment.save()

    LOGGER.info(f'Saving submissions for {assignment}…')
    saveSubmissions(canvasAssignment)

    # LOGGER.info(json.dumps(dictSkipKeys(canvasAssignment, ['_requester']),
    #                        default=str))

    # json.dump(assignmentRubric, open(outputFileName, 'w'),
    #           indent=2, skipkeys=True)

    json.dump(dictSkipKeys(canvasAssignmentRubric, ['_requester']),
              open(outputFileName, 'w'),
              indent=2, skipkeys=True)
    LOGGER.info(f'Assessment raw JSON data saved to file "{outputFileName}".')

    '''
    Rubric objects always contain criteria in the `data` property, and also
    in the `criteria` property when assessments are requested.  Use `data`
    to ensure access to the criteria.
    '''
    # LOGGER.info(f'Rubric criteria from `canvasAssignmentRubric.data`…')
    # LOGGER.info(json.dumps(canvasAssignmentRubric.data, indent=2))

    LOGGER.info('Saving rubric and criteria…')
    rubric, criteria = saveRubricAndCriteria(canvasAssignmentRubric,
                                             canvasAssignment)

    LOGGER.info('Saving assessments and comments…')
    saveAssessmentsAndComments(canvasAssignmentRubric.assessments)

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
