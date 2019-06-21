from django.db import models


class Course(models.Model):
    """
    Represents an instance of a course in a Classroom
    Most fields and options come from the Google API reference:
    https://developers.google.com/classroom/reference/rest/v1/courses
    """
    # Required fields
    name = models.CharField(max_length=750)
    ownerId = models.CharField(max_length=254)
    enrollmentCode = models.CharField(max_length=64)

    # Optional fields
    section = models.CharField(max_length=2800, blank=True)
    descriptionHeading = models.CharField(max_length=3600, blank=True)
    description = models.TextField(max_length=30_000, blank=True)
    room = models.CharField(max_length=650, blank=True)
    alternateLink = models.CharField(max_length=650, blank=True)
    startDate = models.DateTimeField(blank=True)
    endDate = models.DateTimeField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Course state choices enum
    UNSPECIFIED = 'U'
    ACTIVE = 'A'
    ARCHIVED = 'R'
    SUSPENDED = 'S'
    COURSE_STATE_CHOICES = [
        (UNSPECIFIED, 'Unspecified'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
        (SUSPENDED, 'Suspended')
    ]
    courseState = models.CharField(
        max_length=1,
        choices=COURSE_STATE_CHOICES,
        default=UNSPECIFIED
    )

    def __str__(self):
        return self.name
