# standard libaries
import logging

# third-party libraries
from django.db import models

from canvasData import *
from utils import dictOnlyKeys

LOGGER = logging.getLogger(__name__)


class Assessment(models.Model):
    id = models.IntegerField(primary_key=True)


class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course_code = models.TextField()

    @classmethod
    def fromCanvasCourse(cls, course: CanvasCourse) -> User:
        return cls(**dictOnlyKeys(course, ['id', 'name', 'course_code']))

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.course_code}"'


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    sortable_name = models.TextField()
    login_id = models.TextField()

    @classmethod
    def fromCanvasUser(cls, user: CanvasUser) -> User:
        return cls(
            **dictOnlyKeys(user, ['id', 'name', 'sortable_name', 'login_id']))

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.login_id}"'


class Assignment(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasAssignment(cls, assignment: CanvasAssignment) -> User:
        return cls(**dictOnlyKeys(assignment, ['id', 'name', 'course_id']))

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.name}"'


class Rubric(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasRubricAndAssignment(cls, rubric: CanvasRubric,
                                      assignment: CanvasAssignment) -> Rubric:
        return cls(
            **dictOnlyKeys(rubric, ['id', 'title', 'course_id']),
            assignment_id=assignment.id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.title}" ' \
               f'({self.course}; {self.assignment})'


class Submission(models.Model):
    id = models.AutoField(primary_key=True)


class Criterion(models.Model):
    id = models.AutoField(primary_key=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE,
                               related_name='criteria')
