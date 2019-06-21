from django.test import TestCase
from django.urls import reverse


class CourseListViewTests(TestCase):
    # TODO test that the appropriate message is displayed if a user has no courses
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

