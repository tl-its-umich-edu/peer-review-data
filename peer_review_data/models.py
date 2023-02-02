import logging

from django.db import models

from canvasData import *

LOGGER = logging.getLogger(__name__)


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


class Criterion(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField()
    long_description = models.TextField()
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE,
                               related_name='criteria')

    @classmethod
    def fromCanvasCriterionAndRubric(cls, c: CanvasCriteria, r: Rubric):
        # FIXME: Why does returning `Criterion` here cause an error?!
        # It works with other classes.

        criterion: Criterion
        created: bool

        try:
            criterion, created = cls.objects.get_or_create(
                id=c.id,
                description=c.description,
                long_description=c.longDescription,
                rubric=r)
        except Exception as e:
            LOGGER.warning('Error creating Criterion for '
                           f'({c}) and ({r}): {e}')
            # raise e
            return False, False

        return criterion, created

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'"{self.description}" ({self.rubric})'


class Submission(models.Model):
    id = models.IntegerField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasSubmission(cls, s: CanvasSubmission) -> Submission:
        return cls(s.id, s.assignment_id, s.user_id)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assignment}; {self.user})'


class Assessment(models.Model):
    id = models.IntegerField(primary_key=True)
    assessor = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    @classmethod
    def fromCanvasAssessment(cls, a: CanvasAssessment):
        # FIXME: Why does returning `Assessment` here cause an error?!
        # It works with other classes.
        submission: Submission = Submission.objects.get(id=a.submissionId)
        if submission:
            LOGGER.info(f'Got ({submission})!')
        else:
            LOGGER.info(f'Could not find submission with ID ({a.submissionId})!')
        return cls(a.id, a.assessorId, a.submissionId)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assessor}; {self.submission})'


class Comment(models.Model):
    '''
    Strictly speaking, this should be `AssessmentComment`.  This app will
    probably never process any other kind of comment, though, so we'll use
    a short name here for brevity.
    '''
    # Canvas does not give unique IDs for each comment!
    id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    comments = models.TextField()

    @classmethod
    def fromCanvasCommentAndAssessment(cls, c: CanvasComment, a: Assessment):
        # FIXME: Why does returning `Comment` here cause an error?!
        # It works with other classes.
        return cls(None, a.id, c.criterionId, c.comments)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.id}): ' \
               f'({self.assessment}; {self.criterion}; {self.comments})'
