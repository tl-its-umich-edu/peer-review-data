# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from django.utils.timezone import utc

from canvasData import *
from peer_review_data import models

LOGGER: Logger = getLogger(__name__)


def saveCourseAndUsers(course: CanvasCourse) -> bool:
    c = models.Course.fromCanvasCourse(course)
    LOGGER.info(f'Saving {c}…')
    c.save()

    for user in course.get_users():
        u = models.User.fromCanvasUser(user)
        LOGGER.info(f'Saving {u}…')
        u.save()
    return True


def main() -> None:
    timeStart: datetime = datetime.now(tz=utc)
    LOGGER.info(f'Start time: {timeStart.isoformat(timespec="milliseconds")}')

    course: CanvasCourse = canvas.get_course(COURSE_ID)
    LOGGER.info(f'Found course ({course.id}): "{course.name}"')
    courseSaved = False

    # LOGGER.info({k: v for k, v in course.__dict__.items() if k != '_requester'})
    # sys.exit()

    assignment: CanvasAssignment = course.get_assignment(ASSIGNMENT_ID)
    LOGGER.info(f'Found assignment ({assignment.id}): "{assignment.name}"')

    if assignment.peer_reviews is not True:
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'Not configured for peer reviews.')
        sys.exit()

    LOGGER.info(f'Assignment ({assignment.id}) is peer reviewed')

    assignmentRubricId: int = assignment.rubric_settings.get('id')
    LOGGER.info(
        f'Assignment ({assignment.id}) has rubric ID ({assignmentRubricId})')

    outputFileName: str = 'rubric.json'
    assignmentRubric: CanvasRubric = course.get_rubric(
        assignmentRubricId,
        include=['assessments', 'account_associations'], style='full'
    )

    if not hasattr(assignmentRubric, 'assessments'):
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'No peer reviews ("assessments") were found.')
        sys.exit()

    LOGGER.info(f'assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}) has '
                'peer reviews ("assessments")…')

    if not courseSaved:
        pass
        # courseSaved = saveCourseAndUsers(course)

    a = models.Assignment.fromCanvasAssignment(assignment)
    LOGGER.info(f'Saving {a}…')
    a.save()


    LOGGER.info(json.dumps(
        {k: v for k, v in assignment.__dict__.items() if k != '_requester'},
        default=str
    ))
    sys.exit()

    # saveAssignment(assignment)

    # json.dump(assignmentRubric, open(outputFileName, 'w'),
    #           indent=2, skipkeys=True)

    json.dump({k: v for k, v in assignmentRubric.__dict__.items() if
               k != '_requester'}, open(outputFileName, 'w'),
              indent=2, skipkeys=True)
    LOGGER.info(f'Assessment raw JSON data saved to file "{outputFileName}".')

    '''
    Rubric objects always contain criteria in the `data` property, and also
    in the `criteria` property when assessments are requested.  Use `data`
    to ensure access to the criteria.
    '''
    LOGGER.info(json.dumps(assignmentRubric.data, indent=2))

    if not hasattr(assignmentRubric, 'assessments'):
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'No peer reviews ("assessments") were found.')
        sys.exit()

    assessment: CanvasAssessment = CanvasAssessment(
        assignmentRubric.assessments[0])
    LOGGER.info(
        f'**** Assessment 0 --> ID: ({assessment.id}), assessor ID: ({assessment.assessorId})')

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
