# -*- coding: utf-8 -*-
import json
import sys

from canvasData import *

course: CanvasCourse = canvas.get_course(COURSE_ID)
print(f'Found course ({course.id}): "{course.name}"')

assignment: CanvasAssignment = course.get_assignment(ASSIGNMENT_ID)
print(f'Found assignment ({assignment.id}): "{assignment.name}"')

if assignment.peer_reviews is not True:
    print(f'Skipping assignment ({ASSIGNMENT_ID}) in course ({COURSE_ID}): '
          'Not configured for peer reviews.')
    sys.exit()

print(f'Assignment ({assignment.id}) is peer reviewed')

rubricId = assignment.rubric_settings.get('id')

assessmentsRubric: CanvasRubric = course.get_rubric(
    rubricId, include='peer_assessments', style='full')
json.dump(assessmentsRubric.assessments, open('assessments.json', 'w'),
          indent=2)
