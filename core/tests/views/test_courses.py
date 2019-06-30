from django.test import TestCase
from django.urls import reverse

from core.models import Course, CourseWork


class CourseListViewTests(TestCase):
    fixtures = ['classroom', 'course', 'coursework', 'user']

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

    def test_links_work(self):
        course = Course.objects.get(pk=1)
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        course_link = '<a href="%s">' + course.name + '</a>'
        self.assertContains(response, course_link % reverse('course-detail', kwargs={'pk': 1}), html=True)
        self.assertContains(response, '<a href="%s">' % reverse('coursework-detail', kwargs={'pk': 1, 'pk2': 1}))

    def test_all_assignments_listed(self):
        num_of_assignments = CourseWork.objects.filter(course=1).count()
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertContains(response, '<tr class="generic-row">', count=num_of_assignments)
