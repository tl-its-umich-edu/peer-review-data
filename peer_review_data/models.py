# standard libaries
import logging
from datetime import datetime
from typing import Union

# third-party libraries
from django.db import models
from django.db.models.constraints import BaseConstraint


LOGGER = logging.getLogger(__name__)

class Assessment(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Assessment ID')

class User(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='User ID')

class Assignment(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Assignment ID')

class Rubric(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Rubric ID')

class Submission(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Submission ID')

class Criteria(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Criteria ID')
    rubricId = models.ForeignKey(Rubric, on_delete=models.DO_NOTHING)
