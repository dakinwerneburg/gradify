from django.test import TestCase
from django.urls import reverse

from core.models import Course, CourseWork
from users.models import CustomUser


class CourseDetailViewTests(TestCase):
    fixtures = ['course', 'coursework', 'user']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(username='teacher1'))

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
        mock_course: Course = Course.objects.filter(owner=3).first()
        mock_user = mock_course.owner
        self.client.force_login(user=mock_user)
        mock_coursework = mock_course.coursework_set.all().first()
        response = self.client.get(reverse('course-detail', kwargs={'pk': mock_course.id}))
        self.assertContains(response,
                            '<a href="%s">' % reverse('coursework-detail', kwargs={'pk': mock_course.id,
                                                                                   'pk2': mock_coursework.id}))
        self.assertContains(response, '<a href="%s">' %
                            reverse('studentsubmission-list', kwargs={'pk': mock_course.id}))

    def test_all_assignments_listed(self):
        num_of_assignments = CourseWork.objects.filter(course=1).count()
        response = self.client.get(reverse('course-detail', kwargs={'pk': 1}))
        self.assertContains(response, '<tr class="generic-row">', count=num_of_assignments)
