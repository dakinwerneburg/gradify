from django.test import TestCase
from django.urls import reverse

from core.models import CourseWork


class StudentSubmissionListViewTests(TestCase):
    """
    These test aspescts of the student submission view
    """
    fixtures = ['classroom', 'course', 'coursework', 'studentsubmission', 'user']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/course/1/gradebook/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/studentsubmission_list.html')

    def test_all_assignments_listed(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['coursework']) == CourseWork.objects.filter(course_id=1).count())
        self.assertContains(response, response.context['coursework'][0])
        self.assertContains(response, response.context['coursework'][1])

    def test_all_students_listed(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        # TODO change to class roster size after class roster implementation
        self.assertTrue(len(response.context['gradebook']) == 3)
        self.assertContains(response, response.context['gradebook'][0]['student'])
        self.assertContains(response, response.context['gradebook'][1]['student'])

    def test_no_coursework(self):
        """
        If no coursework exists for the course, the appropriate message should be displayed
        """
        CourseWork.objects.all().delete()
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Assignments')
