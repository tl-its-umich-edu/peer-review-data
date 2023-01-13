# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

from django.utils.timezone import utc

from canvasData import *

LOGGER: Logger = getLogger(__name__)


def main() -> None:
    timeStart: datetime = datetime.now(tz=utc)
    LOGGER.info(f'Start time: {timeStart.isoformat(timespec="milliseconds")}')

    course: CanvasCourse = canvas.get_course(COURSE_ID)
    LOGGER.info(f'Found course ({course.id}): "{course.name}"')

    assignment: CanvasAssignment = course.get_assignment(ASSIGNMENT_ID)
    LOGGER.info(f'Found assignment ({assignment.id}): "{assignment.name}"')

    if assignment.peer_reviews is not True:
        LOGGER.info(
            f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
            'Not configured for peer reviews.')
        sys.exit()

    LOGGER.info(f'Assignment ({assignment.id}) is peer reviewed')

    assignmentRubricId: int = assignment.rubric_settings.get('id')
    LOGGER.info(f'**** Assignment Rubric ID --> ({assignmentRubricId})')

    outputFileName: str = 'assessments.json'
    assignmentRubric: CanvasRubric = course.get_rubric(
        assignmentRubricId, include=['assessments', 'account_associations'],
        style='full')
    json.dump(assignmentRubric.assessments, open(outputFileName, 'w'),
              indent=2)
    LOGGER.info(f'Assessment raw JSON data saved to file "{outputFileName}".')

    LOGGER.info(f'{assignmentRubric.assessments[0]}')

    timeEnd: datetime = datetime.now(tz=utc)
    timeElapsed: timedelta = timeEnd - timeStart

    LOGGER.info(f'End time: {timeEnd.isoformat(timespec="milliseconds")}')
    LOGGER.info(f'Elapsed time: {timeElapsed}')
