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
        return cls(**dictOnlyKeys(course.__dict__,
                                  ['id', 'name', 'course_code']))

    def __str__(self) -> str:
        return f'Course ({self.id}): "{self.course_code}"'


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    sortable_name = models.TextField()
    login_id = models.TextField()

    @classmethod
    def fromCanvasUser(cls, user: CanvasUser) -> User:
        return cls(**dictOnlyKeys(user.__dict__,
                                  ['id', 'name', 'sortable_name', 'login_id']))

    def __str__(self) -> str:
        return f'User ({self.id}): "{self.login_id}"'


class Assignment(models.Model):
    id = models.IntegerField(primary_key=True)


class Rubric(models.Model):
    id = models.IntegerField(primary_key=True)


class Submission(models.Model):
    id = models.AutoField(primary_key=True)


class Criteria(models.Model):
    id = models.AutoField(primary_key=True)
    rubricId = models.ForeignKey(Rubric, on_delete=models.DO_NOTHING)
