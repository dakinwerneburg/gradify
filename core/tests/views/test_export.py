from django.test import TestCase
from users.models import CustomUser


class ExportViewTests(TestCase):
    """
    These test aspects of the student submission view
    """
    fixtures = ['course', 'coursework', 'studentsubmission', 'user', 'coursestudent']

    def setUp(self):
        self.client.force_login(CustomUser.objects.get(username='teacher1'))

    # the object headers and http response will be 200 regardless if user has data or not
    # anything else, such as a model change, will result in a server error
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/export/')
        self.assertEqual(response.status_code, 200)
