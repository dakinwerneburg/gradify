from django.test import TestCase
from django.urls import reverse

from core.models import Course


class CourseDetailViewTests(TestCase):
    #  - fields: {name: Current Trends and Projects in Computer Science
    #             section: CMSC 495 6338}
    fixtures = ['course']

    def test_no_course_exist(self):
        # Ensure  a non-existant PK throws a Not Found
        response = self.client.post('courses/1000')
        self.assertEqual(response.status_code, 404)

    def test_course_exist(self):
        # Ensure a valid PK exists and return the correct template
        course = Course.objects.get(pk=1)
        response = self.client.get(reverse('course-detail', args={course.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/course_detail.html')

    def test_course_info(self):
        # Ensure correct course info is displayed
        course = Course.objects.get(pk=1)
        response = self.client.get(reverse('course-detail', args={course.pk}))
        self.assertContains(response, "Current Trends and Projects in Computer Science")
        self.assertContains(response, "CMSC 495 6338")
