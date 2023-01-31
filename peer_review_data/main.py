# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

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


def saveRubricAndCriteria(canvasRubric: CanvasRubric,
                          canvasAssignment: CanvasAssignment):
    rubric = models.Rubric.fromCanvasRubricAndAssignment(canvasRubric,
                                                         canvasAssignment)
    LOGGER.info(f'Saving {rubric}…')
    rubric.save()

    # Get criteria from canvasRubric.data
    for canvasCriterion in canvasRubric.data:
        criterion = models.Criterion.fromCanvasCriterionAndRubric(
            canvasCriterion, rubric)
        LOGGER.info(f'Saving {criterion}…')
        criterion.save()


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
                f'r ID ({assignmentRubricId})')

    outputFileName: str = 'r.json'
    canvasAssignmentRubric: CanvasRubric = canvasCourse.get_rubric(
        assignmentRubricId, include='assessments', style='full')

    if not hasattr(canvasAssignmentRubric, 'assessments'):
        LOGGER.info(f'Skipping assignment ({ASSIGNMENT_ID}) in '
                    f'course ({COURSE_ID}): No peer reviews '
                    '("assessments") found.')
        sys.exit()

    LOGGER.info(f'Assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}) has '
                'peer reviews ("assessments")…')

    if not courseSaved:
        courseSaved, course = saveCourseAndUsers(canvasCourse)

    assignment: models.Assignment = models.Assignment.fromCanvasAssignment(
        canvasAssignment)
    LOGGER.info(f'Saving {assignment}…')
    assignment.save()

    # LOGGER.info(json.dumps(dictSkipKeys(canvasAssignment, ['_requester']),
    #                        default=str))

    # json.dump(assignmentRubric, open(outputFileName, 'w'),
    #           indent=2, skipkeys=True)

    json.dump(dictSkipKeys(canvasAssignmentRubric, ['_requester']),
              open(outputFileName, 'w'),
              indent=2, skipkeys=True)
    LOGGER.info(f'Assessment raw JSON data saved to file "{outputFileName}".')

    if not hasattr(canvasAssignmentRubric, 'assessments'):
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'No peer reviews ("assessments") were found.')
        sys.exit()

    '''
    Rubric objects always contain criteria in the `data` property, and also
    in the `criteria` property when assessments are requested.  Use `data`
    to ensure access to the criteria.
    '''
    LOGGER.info(f'Rubric criteria from `canvasAssignmentRubric.data`…')
    LOGGER.info(json.dumps(canvasAssignmentRubric.data, indent=2))

    saveRubricAndCriteria(canvasAssignmentRubric, canvasAssignment)

    # FIXME: Debugging with first assessment only.  Expand to all assessments.
    assessment: CanvasAssessment = CanvasAssessment(
        canvasAssignmentRubric.assessments[0])
    LOGGER.info(f'**** Assessment 0 --> ID: ({assessment.id}), '
                f'assessor ID: ({assessment.assessorId})')

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
