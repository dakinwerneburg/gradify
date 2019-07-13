from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenCredentialsError

from core.gc_import_utils import *
from core.models import Course
from core.tests.mocks import MockCourse, MockCoursework, MockUser, MockSubmission
from users.models import CustomUser

import logging

# Silence log output during unit tests
logging.getLogger('gradify').setLevel(logging.NOTSET)


class ClassroomIngestViewTests(TestCase):
    fixtures = ['user']

    def setUp(self):
        self.mock_user = CustomUser.objects.get(username='teacher1')
        self.client.force_login(self.mock_user)
        self.mock_gc_course = {
            "id": "12345",
            "name": "Test Course",
            "section": "Test Section",
            "descriptionHeading": "Test Heading",
            "description": "Test description",
            "room": "Test Room",
            "ownerId": "test123",
            "creationTime": "2019-07-05 12:00Z",
            "updateTime": "2019-07-05 12:00Z",
            "enrollmentCode": "thecode",
            "courseState": 'ACTIVE',
            "alternateLink": "https://alink.com",
            "teacherGroupEmail": "group@gmail.com",
            "courseGroupEmail": "group@gmail.com",
            "teacherFolder": {"id": "123", "title": "abc", "alternateLink": "link"},
            "courseMaterialSets": [],
            "guardiansEnabled": True,
            "calendarId": "calId"
        }

    def test_error_msg_if_not_google_user(self):
        """
        The user should be redirected and presented with an error message
        if not signed in with a Google account
        """
        response = self.client.get('/import', follow=True)

        error_msg = response.context['message']
        self.assertTrue('Please Sign In with a Google Account' in error_msg)

    @patch('core.views.ClassroomHelper')
    def test_bad_access_token(self, mock_classroom):
        """
        If the Google user has a bad/invalid access token, an error message
        should be displayed
        """
        instance = mock_classroom.return_value
        instance.is_google_user.return_value = True
        instance.get_courses.side_effect = AccessTokenCredentialsError

        response = self.client.get('/import', follow=True)

        error_msg = response.context['message']
        instance.get_courses.assert_called_once()
        self.assertTrue('Please Sign In with a Google Account' in error_msg)

    @patch('core.views.gc_import_utils.import_course')
    @patch('core.views.ClassroomHelper')
    def test_continues_ingesting_coursework_on_http_error(self, mock_classroom, mock_import_course):
        """
        If the user does not have permissions to view coursework for a given course,
        it should not break the ingest
        """
        gc_instance = mock_classroom.return_value
        gc_instance.is_google_user.return_value = True
        gc_instance.get_courses.return_value = [{'data': 'is_fake'}]
        gc_instance.get_coursework.side_effect = HttpError('', b'')
        mock_import_course.return_value = MockCourse(owner=self.mock_user)

        response = self.client.get('/import', follow=True)

        gc_instance.get_coursework.assert_called()
        self.assertTemplateUsed(response, 'core/course_list.html')

    @patch('core.views.gc_import_utils.import_assignment')
    @patch('core.views.gc_import_utils.import_course')
    @patch('core.views.ClassroomHelper')
    def test_continues_ingesting_students_on_http_error(self, mock_classroom, mock_import_course,
                                                        mock_import_assignment):
        """
        If the user does not have permissions to view students in a given course,
        it should not break the ingest
        """
        gc_instance = mock_classroom.return_value
        gc_instance.is_google_user.return_value = True
        gc_instance.get_courses.return_value = [{'data': 'is_fake'}]
        gc_instance.get_coursework.return_value = self.mock_gc_course
        gc_instance.get_students.side_effect = HttpError('', b'')
        mock_import_course.return_value = MockCourse(owner=self.mock_user)
        mock_import_assignment.returnValue = None

        response = self.client.get('/import', follow=True)

        gc_instance.get_students.assert_called()
        self.assertTemplateUsed(response, 'core/course_list.html')

    @patch('core.views.gc_import_utils.import_student')
    @patch('core.views.gc_import_utils.import_assignment')
    @patch('core.views.gc_import_utils.import_course')
    @patch('core.views.ClassroomHelper')
    def test_continues_ingesting_submissions_on_http_error(self, mock_classroom, mock_import_course,
                                                           mock_import_assignment, mock_import_student):
        """
        If the user does not have permissions to view submissions to a given course,
        it should not break the ingest
        """
        gc_instance = mock_classroom.return_value
        gc_instance.is_google_user.return_value = True
        gc_instance.get_courses.return_value = [{'data': 'is_fake'}]
        gc_instance.get_coursework.return_value = self.mock_gc_course
        gc_instance.get_students.return_value = []
        gc_instance.get_course_submissions.side_effect = HttpError('', b'')
        mock_import_course.return_value = MockCourse(owner=self.mock_user)
        mock_import_assignment.returnValue = None
        mock_import_student.returnValue = None

        response = self.client.get('/import', follow=True)

        gc_instance.get_course_submissions.assert_called()
        self.assertTemplateUsed(response, 'core/course_list.html')

    @patch('core.views.gc_import_utils.import_submission')
    @patch('core.views.gc_import_utils.import_student')
    @patch('core.views.gc_import_utils.import_assignment')
    @patch('core.views.gc_import_utils.import_course')
    @patch('core.views.ClassroomHelper')
    def test_redirects_after_import(self, mock_classroom, mock_import_course, mock_import_assignment,
                                    mock_import_student, mock_import_submission):
        """
        If the API call to GC is successful, the import function should be called
        and the user should be redirected to the course list page
        """
        mock_coursework = MockCoursework(54321, max_points=10)
        gc_instance = mock_classroom.return_value
        gc_instance.is_google_user.return_value = True
        gc_instance.get_courses.return_value = [{'data': 'is_fake'}]
        gc_instance.get_coursework.return_value = [{'data': 'is_fake'}]
        gc_instance.get_students.return_value = [{'data': 'is_fake'}]
        gc_instance.get_course_submissions.return_value = [{'data': 'is_fake'}]
        mock_import_course.return_value = MockCourse(owner=self.mock_user)
        mock_import_assignment.returnValue = mock_coursework
        mock_import_student.returnValue = MockUser(19503)
        mock_import_submission.returnValue = MockSubmission(19503, mock_coursework, 5)

        response = self.client.get('/import', follow=True)

        mock_import_course.assert_called()
        mock_import_assignment.assert_called()
        mock_import_student.assert_called()
        self.assertTemplateUsed(response, 'core/course_list.html')

    def test_import_course_owned_by_user(self):
        """
        Courses owned by the current user should be imported into the database
        with the owner set as the current user
        """
        mock_google_id = SocialAccount.objects.create(user=self.mock_user, provider='Google').uid
        self.mock_gc_course['ownerId'] = mock_google_id

        imported_course = import_course(self.mock_gc_course, self.mock_user)

        self.assertEqual(imported_course.owner_id, self.mock_user.id)

    def test_import_existing_course_user_is_enrolled_in(self):
        """
        Imported courses that already exist in the database but are not owned by the current user
        should result in the user being added as an enrolled student in the course. Any updates to
        course attributes should be updated in the database. The course owner should not be modified.
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google')
        existing_course = Course.objects.create(**filter_course_fields(self.mock_gc_course))

        new_name = 'Updated Course Name'
        self.mock_gc_course['name'] = new_name
        updated_course = import_course(self.mock_gc_course, self.mock_user)

        self.assertEqual(updated_course.owner_id, existing_course.owner_id)
        enrolled_student = updated_course.coursestudent_set.get(student=self.mock_user)
        self.assertTrue(enrolled_student is not None)
        self.assertEqual(updated_course.name, new_name)

    def test_import_new_course_user_is_enrolled_in_gets_default_owner(self):
        """
        If an orphaned course is later imported by its true owner, the database entry should
        be updated accordingly. Enrolled students should not be affected.
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google')

        orphaned_course = import_course(self.mock_gc_course, self.mock_user)

        self.assertEqual(orphaned_course.owner_id, 1)
        self.assertTrue(orphaned_course.coursestudent_set.get(student=self.mock_user) is not None)

    def test_import_orphaned_course_as_owner(self):
        """
        Orphaned courses that exist in the database should have the owner FK
        updated when the true owner imports the course. Enrolled students should
        not be affected
        """
        mock_student = CustomUser.objects.get(username='student1')
        SocialAccount.objects.create(user=mock_student, provider='Google1')
        orphaned_course = import_course(self.mock_gc_course, mock_student)
        self.assertEqual(orphaned_course.owner_id, 1)

        mock_teacher = self.mock_user
        mock_google_id = SocialAccount.objects.create(user=mock_teacher, provider='Google2').uid
        self.mock_gc_course['ownerId'] = mock_google_id
        updated_course = import_course(self.mock_gc_course, mock_teacher)

        self.assertEqual(updated_course.owner, mock_teacher)
        enrolled_student = updated_course.coursestudent_set.get(student=mock_student)
        self.assertTrue(enrolled_student is not None)

    def test_reimporting_orphaned_course_as_enrollee(self):
        """
        If an enrolled student imports an orphaned course that exists in the database, no
        additional enrolled students should be created
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google1')
        orphaned_course = import_course(self.mock_gc_course, self.mock_user)
        self.assertEqual(orphaned_course.owner_id, 1)

        reimported_course = import_course(self.mock_gc_course, self.mock_user)

        self.assertEqual(len(reimported_course.coursestudent_set.all()), 1)

    def test_course_key_filter(self):
        """
        Should filter out course keys we don't use in the database, even if not all filtered
        keys are present
        """
        del self.mock_gc_course['calendarId']
        filtered_course = filter_course_fields(self.mock_gc_course)
        self.assertNotIn('teacherGroupEmail', filtered_course)

    def test_does_not_user_google_id_as_pk(self):
        """
        The Google ID should not be used as the PK. It should be saved as a separate field.
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google1')
        imported_course = import_course(self.mock_gc_course, self.mock_user)
        self.assertNotEqual(imported_course.id, self.mock_gc_course['id'])
        self.assertEqual(imported_course.googleId, self.mock_gc_course['id'])

    def test_properly_sets_course_state(self):
        """
        The course state should be saved
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google1')

        imported_course = import_course(self.mock_gc_course, self.mock_user)
        self.assertEqual(Course.ACTIVE, imported_course.courseState)

        self.mock_gc_course['courseState'] = 'PROVISIONED'
        imported_course = import_course(self.mock_gc_course, self.mock_user)
        self.assertEqual(Course.PROVISIONED, imported_course.courseState)


class AssignmentIngestTests(TestCase):
    fixtures = ['user', 'course']

    def setUp(self):
        self.mock_course = Course.objects.first()
        self.mock_user = CustomUser.objects.get(id=self.mock_course.owner.id)
        self.client.force_login(self.mock_user)
        self.mock_gc_assignment = {
            'courseId': '12345',
            'id': '54321',
            'title': 'Homework 1',
            'description': 'Answer the questions',
            'materials': [],
            'state': 'PUBLISHED',
            'alternateLink': 'https://thelink.com',
            'creationTime': '2019-07-05 12:00Z',
            'updateTime': '2019-07-05 12:00Z',
            'dueDate': {'year': 2019, 'month': 7, 'day': 23},
            'dueTime': {'hours': 11, 'minutes': 30, 'seconds': 0, 'nanos': 0},
            'scheduledTime': '2019-07-05 12:00Z',
            'maxPoints': 10,
            'workType': 'ASSIGNMENT',
            'associatedWithDeveloper': True,
            'assigneeMode': 'ALL_STUDENTS',
            'individualStudentOptions': {},
            'submissionModificationMode': 'MODIFIABLE_UNTIL_TURNED_IN',
            'creatorUserId': '69420',
            'topicId': '1337',
            'assignment': {},
            'multipleChoiceQuestion': {}
        }

    def test_import_assignment(self):
        """
        Assignments should be imported with the course owner set as the author
        """
        saved_assignment: CourseWork = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(saved_assignment.author, self.mock_course.owner)

    def test_reimport_assignment(self):
        """
        Re-imported assignments should update the database
        """
        import_assignment(self.mock_gc_assignment, self.mock_course)
        new_description = 'Answer the essay questions'

        self.mock_gc_assignment['description'] = new_description
        reimported_assignment = import_assignment(self.mock_gc_assignment, self.mock_course)

        self.assertEqual(reimported_assignment.description, new_description)

    def test_assignment_due_date_with_specific_time(self):
        """
        Due dates/times should be correctly created from GC Date and TimeOfDay objects.
        """
        saved_assignment: CourseWork = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(saved_assignment.dueDate, "2019-07-23 11:30:00.000Z")

    def test_assignment_due_date_with_default_time(self):
        """
        If there is no due time specified, dueDate field should default to 23:59:59:999 on the due date
        """
        del self.mock_gc_assignment['dueTime']
        saved_assignment: CourseWork = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(saved_assignment.dueDate, "2019-07-23 23:59:59.999Z")

    def test_no_due_date(self):
        """
        Assignments should still be saved with a blank due date if no due date is provided
        """
        del self.mock_gc_assignment['dueDate']
        del self.mock_gc_assignment['dueTime']
        saved_assignment: CourseWork = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(saved_assignment.dueDate, None)

    def test_does_not_user_google_id_as_pk(self):
        """
        The Google ID should not be used as the PK. It should be saved as a separate field.
        """
        imported_assignment = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertNotEqual(imported_assignment.id, self.mock_gc_assignment['id'])
        self.assertEqual(imported_assignment.googleId, self.mock_gc_assignment['id'])

    def test_properly_converts_enum_fields(self):
        imported_assignment = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(CourseWork.PUBLISHED, imported_assignment.state)
        self.assertEqual(CourseWork.ASSIGNMENT, imported_assignment.workType)

        self.mock_gc_assignment['state'] = 'PUBLISHED'
        imported_assignment = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(CourseWork.PUBLISHED, imported_assignment.state)

    def test_import_uses_default_for_unknown_enum_val(self):
        self.mock_gc_assignment['state'] = 'IDAHO'
        imported_assignment = import_assignment(self.mock_gc_assignment, self.mock_course)
        self.assertEqual(CourseWork.COURSE_WORK_STATE_UNSPECIFIED, imported_assignment.state)


class StudentIngestTests(TestCase):
    fixtures = ['user', 'course']

    def setUp(self):
        self.mock_course: Course = Course.objects.first()
        self.mock_student: CustomUser = CustomUser.objects.first()
        self.client.force_login(self.mock_student)
        self.mock_gc_student = {
            'courseId': str(self.mock_course.id),
            'userId': self.mock_student.email,
            'profile': {
                'id': '12345',  # Google ID used to check if acct exists
                'name': {'givenName': 'John', 'familyName': 'Doe', 'fullName': 'John Doe'},
                'emailAddress': 'john.doe@gmail.com',
                'photoUrl': 'https://someLink',
                'permissions': [],
                'verifiedTeacher': False
            },
            'studentWorkFolder': {}
        }

    def test_ingest_new_student_no_acct(self):
        """
        If the student does not have an account in the database, one should be created
        and the new user should be enrolled as a CourseStudent
        """
        expected_first_name = self.mock_gc_student['profile']['name']['givenName']
        expected_last_name = self.mock_gc_student['profile']['name']['familyName']
        expected_email_addr = self.mock_gc_student['profile']['emailAddress']

        import_student(self.mock_gc_student, self.mock_course)

        new_acct = SocialAccount.objects.get(uid=self.mock_gc_student['profile']['id']).user
        self.assertEqual(new_acct.first_name, expected_first_name)
        self.assertEqual(new_acct.last_name, expected_last_name)
        self.assertEqual(new_acct.email, expected_email_addr)

        new_enrollment = CourseStudent.objects.get(student=new_acct, course=self.mock_course)
        self.assertTrue(new_enrollment is not None)

    def test_ingest_multiple_students(self):
        """
        The app should be able to import multiple students without issue
        """
        og_student_count = len(CourseStudent.objects.filter(course=self.mock_course))
        student1 = self.mock_gc_student
        student2 = {
            'courseId': str(self.mock_course.id),
            'userId': 'student2@gmail.com',
            'profile': {
                'id': '69420',  # Google ID used to check if acct exists
                'name': {'givenName': 'Teddy', 'familyName': 'Userman', 'fullName': 'Teddy Userman'},
                'emailAddress': 'ted@gmail.com',
                'photoUrl': 'https://someLink',
                'permissions': [],
                'verifiedTeacher': False
            },
            'studentWorkFolder': {}
        }

        import_student(student1, self.mock_course)
        import_student(student2, self.mock_course)

        new_student_count = len(CourseStudent.objects.filter(course=self.mock_course))
        self.assertTrue(new_student_count == og_student_count + 2)

    def test_acct_exists_but_student_is_new(self):
        """
        If a student being imported has an existing user account, the existing
        account should be used to enroll the student (no new acct created)
        """
        existing_acct = SocialAccount.objects.create(uid=self.mock_gc_student['profile']['id'], provider='google',
                                                     user=self.mock_student).user
        og_acct_count = len(CustomUser.objects.all())

        new_enrollment = import_student(self.mock_gc_student, self.mock_course)

        self.assertEqual(new_enrollment.student, existing_acct)
        self.assertEqual(len(CustomUser.objects.all()), og_acct_count)

    def test_student_exists_and_is_enrolled(self):
        """
        If the student is already enrolled with a valid account, no action is necessary
        """
        SocialAccount.objects.create(uid=self.mock_gc_student['profile']['id'], provider='google',
                                     user=self.mock_student)
        CourseStudent.objects.create(student=self.mock_student, course=self.mock_course)

        imported_enrollment = import_student(self.mock_gc_student, self.mock_course)

        self.assertEqual(self.mock_student, imported_enrollment.student)

    def test_import_can_later_be_viewed_by_new_user(self):
        """
        A submission should be associated with a user if the user signs in after the submission is imported
        """
        import_student(self.mock_gc_student, self.mock_course)
        new_acct = SocialAccount.objects.get(uid=self.mock_gc_student['profile']['id']).user
        self.client.force_login(new_acct)

        response = self.client.get(reverse('course-list'))

        self.assertContains(response, self.mock_course)


class SubmissionIngestTests(TestCase):
    fixtures = ['user', 'course', 'coursework']

    def setUp(self):
        self.mock_course = Course.objects.first()
        self.mock_coursework = CourseWork.objects.filter(course=self.mock_course).first()
        self.mock_student = CustomUser.objects.first()
        self.mock_gc_submission = {
            'courseId': str(self.mock_course.id),
            'courseWorkId': str(self.mock_coursework.googleId),
            'id': 'Cg4IjpW9iYoBEIrS6qSKAQ',
            'userId': '12345',  # Google ID
            'creationTime': '',
            'updateTime': '',
            'state': 'RETURNED',
            'late': False,
            'draftGrade': 8,
            'assignedGrade': 8,
            'alternateLink': 'https://somelink',
            'courseWorkType': 'ASSIGNMENT',
            'associatedWithDeveloper': True,
            'submissionHistory': [],
            'assignmentSubmission': {},
            'shortAnswerSubmission': {},
            'multipleChoiceSubmission': {}
        }
        SocialAccount.objects.create(uid=self.mock_gc_submission['userId'], provider='google', user=self.mock_student)

    def test_import_new_submission(self):
        """
        New submissions should be saved to the database
        """
        og_submission_count = len(
            StudentSubmission.objects.filter(coursework__googleId=self.mock_gc_submission['courseWorkId']))

        import_submission(self.mock_gc_submission)

        updated_submission_count = len(
            StudentSubmission.objects.filter(coursework__googleId=self.mock_gc_submission['courseWorkId']))
        self.assertEqual(og_submission_count + 1, updated_submission_count)

    def test_import_existing_submission(self):
        """
        Importing a submission that already exists in the database should have no effect
        """
        existing_submission = import_submission(self.mock_gc_submission)
        og_submission_count = len(
            StudentSubmission.objects.filter(coursework_id=self.mock_gc_submission['courseWorkId']))

        resubmission = import_submission(self.mock_gc_submission)

        updated_submission_count = len(
            StudentSubmission.objects.filter(coursework_id=self.mock_gc_submission['courseWorkId']))
        self.assertEqual(og_submission_count, updated_submission_count)
        self.assertEqual(existing_submission, resubmission)

    def test_import_multiple_submissions(self):
        """
        Multiple submissions should be imported without issue
        """
        mock_google_id = 69420
        og_submission_count = len(StudentSubmission.objects.filter(coursework=self.mock_coursework))
        SocialAccount.objects.create(uid=mock_google_id, provider='google', user=CustomUser.objects.all()[1])
        submission1 = self.mock_gc_submission
        submission2 = {
            'courseId': str(self.mock_course.id),
            'courseWorkId': str(self.mock_coursework.googleId),
            'id': 'asdfasfda01924',
            'userId': mock_google_id,  # Google ID
            'creationTime': '',
            'updateTime': '',
            'state': 'RETURNED',
            'late': False,
            'draftGrade': 8,
            'assignedGrade': 8,
            'alternateLink': 'https://somelink',
            'courseWorkType': 'ASSIGNMENT',
            'associatedWithDeveloper': True,
            'submissionHistory': [],
            'assignmentSubmission': {},
            'shortAnswerSubmission': {},
            'multipleChoiceSubmission': {}
        }

        import_submission(submission1)
        import_submission(submission2)

        new_submission_count = len(StudentSubmission.objects.filter(coursework=self.mock_coursework))
        self.assertEqual(new_submission_count, og_submission_count + 2)

    def test_properly_converts_enum_fields(self):
        imported_submission = import_submission(self.mock_gc_submission)
        self.assertEqual(StudentSubmission.RETURNED, imported_submission.state)
        self.assertEqual(CourseWork.ASSIGNMENT, imported_submission.courseWorkType)
