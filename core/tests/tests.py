from django.test import TestCase
from django.urls import reverse

from ..models import Course, CourseWork, StudentSubmission


class CourseListViewTests(TestCase):
    fixtures = ['courses']

    def test_course_list(self):
        """
        If courses exist, the names should be displayed
        """
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        course_names = [course.name for course in response.context['course_list']]
        self.assertContains(response, course_names[0])
        self.assertContains(response, course_names[1])

    def test_no_courses(self):
        """
        If no courses exist, the appropriate message should be displayed
        """
        Course.objects.all().delete()
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No courses found')


class StudentSubmissionListViewTests(TestCase):
    """
    These test aspescts of the student submission view
    """
    fixtures = ['classroom', 'courses', 'coursework', 'studentsubmission', 'user']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/courses/gradebook/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/studentsubmission_list.html')

    def test_all_assignments_listed(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['coursework']) == CourseWork.objects.filter(course_id=1).count())
        self.assertContains(response, response.context['coursework'][0])
        self.assertContains(response, response.context['coursework'][1])

    def test_all_students_listed(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        # TODO change to class roster size after class roster implementation
        self.assertTrue(len(response.context['gradebook']) == 3)
        # TODO test iteration of students

    def test_no_student_submissions(self):
        """
        If no student submissions exist, the appropriate message should be displayed
        """
        StudentSubmission.objects.all().delete()
        CourseWork.objects.all().delete()
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No student submissions')
