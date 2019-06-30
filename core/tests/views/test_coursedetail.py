from django.test import TestCase
from django.urls import reverse

from core.models import Course, CourseWork


class CourseDetailViewTests(TestCase):
    fixtures = ['classroom', 'course', 'coursework', 'user']

    def test_no_course_exist(self):
        response = self.client.post('course/1000')
        self.assertEqual(response.status_code, 404)

    def test_course_exist(self):
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/course_detail.html')

    def test_course_info(self):
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertContains(response, "Current Trends and Projects in Computer Science")
        self.assertContains(response, "CMSC 495 6338")

    def test_no_coursework(self):
        CourseWork.objects.all().delete()
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Assignments')

    def test_links_work(self):
        course = Course.objects.get(pk=1)
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        course_link = '<a href="%s">' + course.name + '</a>'
        self.assertContains(response, course_link % reverse('course-detail', kwargs={'pk': 1}), html=True)
        self.assertContains(response, '<a href="%s">' % reverse('coursework-detail', kwargs={'pk': 1, 'pk2': 1}))
        self.assertContains(response, '<a href="%s">View/Edit Gradebook</a>' % 
                            reverse('studentsubmission-list', kwargs={'pk': 1}), html=True)

    def test_all_assignments_listed(self):
        num_of_assignments = CourseWork.objects.filter(course=1).count()
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertContains(response, '<tr class="generic-row">', count=num_of_assignments)
