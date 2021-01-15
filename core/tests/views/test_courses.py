from django.test import TestCase
from django.urls import reverse

from core.models import Course, CourseWork, CourseStudent
from users.models import CustomUser


class CourseListViewTests(TestCase):
    fixtures = ['course', 'coursework', 'user']

    def setUp(self):
        self.test_user = CustomUser.objects.get(username='teacher1')
        self.client.force_login(self.test_user)

    def test_course_list(self):
        """
        If courses exist, the names should be displayed
        """
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        course_names = [course.name for course in response.context['course_list']]
        self.assertContains(response, course_names[0])
        self.assertContains(response, course_names[1])

    def test_owned_and_enrolled_courses_not_listed(self):
        """
        The course list should contain courses that the user owns and not courses
        that the user is enrolled in
        """
        Course.objects.all().delete()
        owned_course = Course.objects.create(name='Owned Course', enrollmentCode='12345', owner=self.test_user)
        enrolled_course = Course.objects.create(name='Enrolled Course', enrollmentCode='12345')
        CourseStudent.objects.create(student=self.test_user, course=enrolled_course)

        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, owned_course)
        self.assertNotContains(response, enrolled_course)

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
