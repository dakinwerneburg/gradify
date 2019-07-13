from django.db import models


class Course(models.Model):
    """
    Represents an instance of a course in a Classroom
    Most fields and options come from the Google API reference:
    https://developers.google.com/classroom/reference/rest/v1/courses
    """
    # Required fields
    name = models.CharField(max_length=750)
    enrollmentCode = models.CharField(max_length=64)

    # Owner may be set to the default if a user imports a course for which the user is not the owner
    # If the actual owner later imports the same course, the owner field will be updated
    owner = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE, default=1)

    # Optional fields
    section = models.CharField(max_length=2800, blank=True)
    descriptionHeading = models.CharField(max_length=3600, blank=True, verbose_name="Heading")
    description = models.TextField(max_length=30_000, blank=True)
    room = models.CharField(max_length=650, blank=True)
    alternateLink = models.CharField(max_length=650, blank=True, verbose_name="Link")
    startDate = models.DateTimeField(blank=True, null=True, verbose_name="Start Date")
    endDate = models.DateTimeField(blank=True, null=True, verbose_name="End Date")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Google Classroom specific
    googleId = models.CharField(max_length=32, blank=True, null=True)
    creationTime = models.DateTimeField(blank=True, null=True)
    updateTime = models.DateTimeField(blank=True, null=True)
    ownerId = models.CharField(max_length=254)

    # Course state choices enum
    COURSE_STATE_UNSPECIFIED = 'COURSE_STATE_UNSPECIFIED'
    ACTIVE = 'ACTIVE'
    ARCHIVED = 'ARCHIVED'
    PROVISIONED = 'PROVISIONED'
    DECLINED = 'DECLINED'
    SUSPENDED = 'SUSPENDED'
    COURSE_STATE_CHOICES = [
        (COURSE_STATE_UNSPECIFIED, 'Unspecified'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived'),
        (PROVISIONED, 'Provisioned'),
        (DECLINED, 'Declined'),
        (SUSPENDED, 'Suspended')
    ]
    courseState = models.CharField(
        max_length=64,
        choices=COURSE_STATE_CHOICES,
        default=COURSE_STATE_UNSPECIFIED
    )

    def __str__(self):
        return self.name


class CourseWork(models.Model):
    """
    Course work created by a teacher for students of the course.
    https://developers.google.com/classroom/reference/rest/v1/courses.courseWork
    """

    # Required Fields
    course = models.ForeignKey(to='Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=750)
    author = models.ForeignKey(to='users.CustomUser', on_delete=models.SET_NULL, null=True)

    # Optional Fields
    googleId = models.TextField(max_length=32, blank=True, null=True)
    description = models.TextField(max_length=30_000, blank=True)
    alternateLink = models.TextField(max_length=650, blank=True)
    maxPoints = models.IntegerField(blank=True, verbose_name="Max Points")
    dueDate = models.DateTimeField(blank=True, null=True, verbose_name="Due Date")
    creationTime = models.DateTimeField(blank=True, null=True)
    updateTime = models.DateTimeField(blank=True, null=True)
    creatorUserId = models.CharField(max_length=254)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Course work state choices enum
    COURSE_WORK_STATE_UNSPECIFIED = 'COURSE_WORK_STATE_UNSPECIFIED'
    PUBLISHED = 'PUBLISHED'
    DRAFT = 'DRAFT'
    DELETED = 'DELETED'
    COURSE_WORK_STATE_CHOICES = [
        (COURSE_WORK_STATE_UNSPECIFIED, 'Unspecified'),
        (PUBLISHED, 'Published'),
        (DRAFT, 'Draft'),
        (DELETED, 'Deleted'),
    ]
    state = models.CharField(
        max_length=64,
        choices=COURSE_WORK_STATE_CHOICES,
        default=COURSE_WORK_STATE_UNSPECIFIED
    )

    # Course work type choices enum
    COURSE_WORK_TYPE_UNSPECIFIED = 'COURSE_WORK_TYPE_UNSPECIFIED'
    ASSIGNMENT = 'ASSIGNMENT'
    SHORT_ANSWER_QUESTION = 'SHORT_ANSWER_QUESTION'
    MULTIPLE_CHOICE_QUESTION = 'MULTIPLE_CHOICE_QUESTION'
    COURSE_WORK_TYPE_CHOICES = [
        (COURSE_WORK_TYPE_UNSPECIFIED, 'Unspecified'),
        (ASSIGNMENT, 'Assignment'),
        (SHORT_ANSWER_QUESTION, 'Short Answer Question'),
        (MULTIPLE_CHOICE_QUESTION, 'Multiple Choice Question'),
    ]
    workType = models.CharField(
        max_length=64,
        choices=COURSE_WORK_TYPE_CHOICES,
        default=COURSE_WORK_TYPE_UNSPECIFIED,
        verbose_name="Work Type"
    )

    # Course Work Source enum
    COURSE_WORK_SOURCE_UNSPECIFIED = 'U'
    GOOGLE = 'C'
    GRADIFY = 'G'
    COURSE_WORK_SOURCE_CHOICES = [
        (COURSE_WORK_SOURCE_UNSPECIFIED, 'Unspecified'),
        (GOOGLE, 'Google Classroom'),
        (GRADIFY, 'Gradify'),
    ]
    source = models.CharField(
        max_length=1,
        choices=COURSE_WORK_SOURCE_CHOICES,
        default=COURSE_WORK_SOURCE_UNSPECIFIED
    )

    def __str__(self):
        return self.title


class StudentSubmission(models.Model):
    """
    This model represents course work items that
    have been completed by students.
    https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions
    """

    # Required Fields
    student = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE)
    coursework = models.ForeignKey(to='CourseWork', on_delete=models.CASCADE)

    # Optional Fields
    late = models.BooleanField(default=False)
    draftGrade = models.FloatField(blank=True, null=True)
    assignedGrade = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    alternateLink = models.TextField(max_length=650, blank=True)

    # GC specific
    gcSubmissionId = models.TextField(max_length=650, blank=True)

    # Student submission state choices enum
    SUBMISSION_STATE_UNSPECIFIED = 'SUBMISSION_STATE_UNSPECIFIED'
    NEW = 'NEW'
    CREATED = 'CREATED'
    TURNED_IN = 'TURNED_IN'
    RETURNED = 'RETURNED'
    RECLAIMED_BY_STUDENT = 'RECLAIMED_BY_STUDENT'

    SUBMISSION_STATE_CHOICES = [
        (SUBMISSION_STATE_UNSPECIFIED, 'Unspecified'),
        (NEW, 'New'),
        (CREATED, 'Created'),
        (TURNED_IN, 'Turned In'),
        (RETURNED, 'Returned'),
        (RECLAIMED_BY_STUDENT, 'Reclaimed by Student'),
    ]
    state = models.CharField(
        max_length=64,
        choices=SUBMISSION_STATE_CHOICES,
        default=SUBMISSION_STATE_UNSPECIFIED
    )

    COURSE_WORK_TYPE_UNSPECIFIED = 'COURSE_WORK_TYPE_UNSPECIFIED'
    ASSIGNMENT = 'ASSIGNMENT'
    SHORT_ANSWER_QUESTION = 'SHORT_ANSWER_QUESTION'
    MULTIPLE_CHOICE_QUESTION = 'MULTIPLE_CHOICE_QUESTION'
    COURSEWORK_TYPE_CHOICES = [
        (COURSE_WORK_TYPE_UNSPECIFIED, 'Unspecified'),
        (ASSIGNMENT, 'Assignment'),
        (SHORT_ANSWER_QUESTION, 'Short Answer Question'),
        (MULTIPLE_CHOICE_QUESTION, 'Multiple Choice Question'),
    ]
    courseWorkType = models.CharField(
        max_length=64,
        choices=COURSEWORK_TYPE_CHOICES,
        default=COURSE_WORK_TYPE_UNSPECIFIED
    )

    def __str__(self):
        return "%s: %s - %s" % (self.id, self.student, self.coursework)


class CourseStudent(models.Model):
    # Required Fields
    student = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE)
    course = models.ForeignKey(to='Course', on_delete=models.CASCADE)

    # Optional Fields
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%d: %s - %s" % (self.id, self.student, self.course)
