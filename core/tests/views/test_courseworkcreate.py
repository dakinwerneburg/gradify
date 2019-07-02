from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from core.views import CoursesView
from users.models import CustomUser


class CourseWorkCreateTests(TestCase):
    fixtures = ['classroom', 'course', 'coursework', 'user']

    def setUp(self):
        # Provide intial login information.
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(
            username='tester', email='tester@gmail.com', password='top_secret')
        c = Client()
        c.login(username='tester', password='top_secret')

    def test_user_login(self):
        request = self.factory.get('/course/')
        request.user = self.user
        response = CoursesView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_quick_link_exists(self):
        response = self.client.get(reverse('course-list'))
        self.assertContains(response, '<h1 class="bg-header">Quick Links</h1>')

    def test_new_assignment_link_exists(self):
        response = self.client.get(reverse('course-list'))
        self.assertContains(response, '<a href="%s">' % reverse('coursework-create'))
