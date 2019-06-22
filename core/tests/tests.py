from django.test import TestCase
from django.urls import reverse

from ..models import Course


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
