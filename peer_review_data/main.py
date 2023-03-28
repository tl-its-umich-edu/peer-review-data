# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

import sys
from django.utils.timezone import utc

from canvasData import *
from peer_review_data import models
from utils import dictSkipKeys

LOGGER: Logger = getLogger(__name__)


def saveCourseAndUsers(canvasCourse: CanvasCourse) -> (bool, Course):
    course = models.Course.fromCanvasCourse(canvasCourse)
    LOGGER.info(f'Saving {course}…')
    course.save()

    LOGGER.info(f'Saving users of {course}…')
    for canvasUser in canvasCourse.get_users(**{'include[]': 'test_student'}):
        try:
            user = models.User.fromCanvasUser(canvasUser)
            LOGGER.debug(f'Saving {user}…')
            user.save()
        except Exception as e:
            LOGGER.warning(f'Error saving {user}: {e}')

    return True, course


def saveSubmissions(canvasAssignment: CanvasAssignment):
    canvasSubmissions: List[CanvasSubmission] = \
        canvasAssignment.get_submissions()

    for canvasSubmission in canvasSubmissions:
        '''
        The only untyped submission found during development was from
        "Test Student".  It was discovered because that student wasn't
        included with the rest of the course users and the relationship
        between submission and missing user couldn't be created.  Testing
        for untyped submissions eliminates those from "Test Student" and
        possibly others.
        '''
        # if canvasSubmission.submission_type is None:
        #     LOGGER.warning('Skipping untyped submission '
        #                    f'({canvasSubmission.id}) for '
        #                    f'user ID ({canvasSubmission.user_id}).')
        #     continue

        try:
            submission: models.Submission = \
                models.Submission.fromCanvasSubmission(canvasSubmission)
            LOGGER.debug(f'Saving {submission}…')
            submission.save()
        except Exception as e:
            LOGGER.warning(f'Error saving Submission: {e}')
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

    '''
    Rubric objects always contain criteria in the `data` property, and also
    in the `criteria` property when assessments are requested.  Use `data`
    to ensure access to the criteria.
    '''
    for canvasCriterion in canvasRubric.data:
        criterion = models.Criterion.fromCanvasCriterionAndRubric(
            CanvasCriteria(canvasCriterion), rubric)
        LOGGER.info(f'Saving {criterion}…')
        criterion.save()
        criteria[criterion.id] = criterion

    return rubric, criteria


def saveAssessmentsAndComments(
        canvasAssessments: List[CanvasAssessment]) -> None:
    """
    Given a list of `CanvasAssessment` objects, skip those that are not
    peer reviews and save the rest.  When saving assessments, save their
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

        if assessment:
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


def main() -> None:
    timeStart: datetime = datetime.now(tz=utc)
    LOGGER.info(f'Start time: {timeStart.isoformat(timespec="milliseconds")}')

    courseId: str
    for courseId in config.COURSE_IDS_CSV.split(','):
        canvasCourse: CanvasCourse = canvas.get_course(courseId)
        LOGGER.info(f'Found course ({canvasCourse.id}): "{canvasCourse.name}"')
        courseSaved = False
        course: models.Course | None = None
        user: models.User | None = None

        canvasAssignments: List[CanvasAssignment] = canvasCourse.get_assignments()

        canvasAssignment: CanvasAssignment = None
        for a in filter(lambda a: a.peer_reviews, canvasAssignments):
            LOGGER.info(
                f'Assignment ({a.id}), "{a.name}" has peer reviews: {a.peer_reviews}')

            # if not canvasAssignment:
            #     canvasAssignment = a
            canvasAssignment = a

            # LOGGER.info(json.dumps(
            #     dictSkipKeys(
            #         a,
            #         ['type', '_requester']),
            #     indent=2, default=str))

            # canvasAssignment: CanvasAssignment = canvasCourse.get_assignment(
            #     assignmentId)
            LOGGER.info(
                f'Found assignment ({canvasAssignment.id}): "{canvasAssignment.name}"')

            if canvasAssignment.peer_reviews is not True:
                LOGGER.info(
                    f'Skipping assignment ({canvasAssignment.id}) '
                    f'in course ({courseId}): '
                    'Not configured for peer reviews.')
                sys.exit()

            LOGGER.info(f'Assignment ({canvasAssignment.id}) is peer reviewed')

            assignmentRubricId: int = canvasAssignment.rubric_settings.get('id')
            LOGGER.info(f'Assignment ({canvasAssignment.id}) has '
                        f'rubric ID ({assignmentRubricId})')

            canvasAssignmentRubric: CanvasRubric = canvasCourse.get_rubric(
                assignmentRubricId, include='assessments', style='full')

            # json.dump(dictSkipKeys(canvasAssignmentRubric, ['_requester']),
            #           open('rubric.json', 'w'), indent=2, skipkeys=True)
            # sys.exit()

            if not hasattr(canvasAssignmentRubric, 'assessments'):
                # LOGGER.info(f'Skipping assignment ({assignmentId}) in '
                LOGGER.info(f'Skipping assignment ({canvasAssignment.id}) in '
                            f'course ({courseId}): '
                            'Not configured for peer reviews ("assessments").')
                sys.exit()

            LOGGER.info(f'Assignment ({canvasAssignment.id}) '
                        f'in course ({courseId}) is '
                        'configured for peer reviews ("assessments")…')

            if len(canvasAssignmentRubric.assessments) == 0:
                LOGGER.info(
                    f'Skipping assignment ({canvasAssignment.id}) '
                    f'in course ({courseId}): '
                    'No peer reviews ("assessments") were found.')
                sys.exit()

            LOGGER.info(f'Assignment ({canvasAssignment.id}) '
                        f'in course ({courseId}) has '
                        'peer reviews ("assessments")…')

            if not courseSaved:
                courseSaved, course = saveCourseAndUsers(canvasCourse)

            assignment: models.Assignment = models.Assignment.fromCanvasAssignment(
                canvasAssignment)
            LOGGER.info(f'Saving {assignment}…')
            assignment.save()

            LOGGER.info(f'Saving submissions for {assignment}…')
            saveSubmissions(canvasAssignment)

            LOGGER.info('Saving rubric and criteria…')
            rubric, criteria = saveRubricAndCriteria(canvasAssignmentRubric,
                                                     canvasAssignment)

            LOGGER.info('Saving assessments and comments…')
            saveAssessmentsAndComments(canvasAssignmentRubric.assessments)

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
