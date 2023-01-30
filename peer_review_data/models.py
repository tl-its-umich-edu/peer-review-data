import logging

from django.db import models

from canvasData import *
from utils import dictKeepKeys

LOGGER = logging.getLogger(__name__)


class Assessment(models.Model):
    id = models.IntegerField(primary_key=True)


class Course(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course_code = models.TextField()

    @classmethod
    def fromCanvasCourse(cls, c: CanvasCourse) -> Course:
        return cls(c.id, c.name, c.course_code)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.course_code}"'


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    sortable_name = models.TextField()
    login_id = models.TextField()

    @classmethod
    def fromCanvasUser(cls, u: CanvasUser) -> User:
        return cls(u.id, u.name, u.sortable_name, u.login_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.login_id}"'


class Assignment(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasAssignment(cls, a: CanvasAssignment) -> Assignment:
        return cls(a.id, a.name, a.course_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.name}"'


class Rubric(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasRubricAndAssignment(cls, r: CanvasRubric,
                                      a: CanvasAssignment) -> Rubric:
        return cls(r.id, r.title, r.course_id, a.id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): "{self.title}" ' \
               f'({self.course}; {self.assignment})'


class Submission(models.Model):
    id = models.AutoField(primary_key=True)


class Criterion(models.Model):
    id = models.AutoField(primary_key=True)
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE,
                               related_name='criteria')

    @classmethod
    def fromCanvasCriterion(cls, criterion: dict):
        # def fromCanvasCriterion(cls, criterion: dict) -> Criterion:
        # FIXME: Why is returning `Criterion` here an error?!
        # It works with other classes.
        return cls(
            **dictKeepKeys(criterion, ['id', 'title', 'course_id']))
        # TODO: Continue…
