from django.test import TestCase
from django.urls import reverse


class CourseDeleteViewTests(TestCase):
    fixtures = ['classroom', 'course', 'coursework', 'user']

    def test_my_get_request(self):
        response = self.client.get(reverse('course-delete', args=(1,)), follow=True)
        self.assertContains(response, 'Are you sure you want to delete')

    def test_my_post_request(self):
        post_response = self.client.post(reverse('course-delete', args=(1,)), follow=True)
        self.assertRedirects(post_response, '/?next=/course/', status_code=302)
