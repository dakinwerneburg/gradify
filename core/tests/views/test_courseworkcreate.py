from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class CourseWorkCreateTests(TestCase):
    fixtures = ['classroom', 'course', 'coursework', 'user']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(username='teacher1'))

    def test_quick_link_exists(self):
        response = self.client.get(reverse('course-list'))
        self.assertContains(response, '<h1 class="bg-header">Quick Links</h1>')

    def test_new_assignment_link_exists(self):
        response = self.client.get(reverse('course-list'))
        self.assertContains(response, '<a href="%s">' % reverse('coursework-create'))
