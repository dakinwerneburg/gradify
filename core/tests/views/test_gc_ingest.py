from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from django.test import TestCase
from oauth2client.client import AccessTokenCredentialsError

from core.gc_import_utils import import_course, filter_course_fields
from core.models import Course
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
            "courseState": 1,
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
    def test_redirects_after_import(self, mock_classroom, mock_import):
        """
        If the API call to GC is successful, the import function should be called
        and the user should be redirected to the course list page
        """
        gc_instance = mock_classroom.return_value
        gc_instance.is_google_user.return_value = True
        gc_instance.get_courses.return_value = [{'data': 'is_fake'}]
        mock_import.return_value = None

        response = self.client.get('/import', follow=True)

        mock_import.assert_called()
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
        should result in the user being added as an enrolled student in the course. The course
        owner should not be modified.
        """
        SocialAccount.objects.create(user=self.mock_user, provider='Google')
        existing_course = Course.objects.create(**filter_course_fields(self.mock_gc_course))

        imported_course = import_course(self.mock_gc_course, self.mock_user)

        self.assertEqual(imported_course.owner_id, existing_course.owner_id)
        enrolled_student = imported_course.coursestudent_set.get(student=self.mock_user)
        self.assertTrue(enrolled_student is not None)

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
        Imported courses that do not exist in the database and are not owned by the current user
        should be created as "orphaned" courses with a default owner of 1 (id of the admin user).
        The user should then be enrolled in the course
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
