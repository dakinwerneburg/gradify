from django.test import TestCase
from django.urls import reverse

from core.models import CourseWork
from users.models import CustomUser


class CourseWorkDetailViewTests(TestCase):

    fixtures = ['classroom', 'course', 'coursework', 'user']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(username='teacher1'))

    def test_coursework_exists(self):
        response = self.client.get('/course/1/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/coursework_detail.html')

    def test_coursework_does_not_exists(self):
        response = self.client.get('/course/1/100/')
        self.assertEqual(response.status_code, 404)

    def test_correct_coursework_displayed(self):
        coursework = CourseWork.objects.get(pk=1)
        response = self.client.get(reverse('coursework-detail', kwargs={'pk': 1, 'pk2': 1}))
        self.assertContains(response, coursework.title)
