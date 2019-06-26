from django.test import TestCase
from django.urls import reverse

from ..models import Course, CourseWork, StudentSubmission, CourseStudent


class CourseListViewTests(TestCase):
    fixtures = ['courses']

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


class StudentSubmissionListViewTests(TestCase):
    """
    These test aspescts of the student submission view
    """
    fixtures = ['classroom', 'courses', 'coursework', 'studentsubmission', 'user']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/courses/gradebook/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/studentsubmission_list.html')

    def test_all_assignments_listed(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['coursework']) == CourseWork.objects.filter(course_id=1).count())
        self.assertContains(response, response.context['coursework'][0])
        self.assertContains(response, response.context['coursework'][1])

    def test_all_students_listed(self):
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        # TODO change to class roster size after class roster implementation
        self.assertTrue(len(response.context['gradebook']) == 3)
        # TODO test iteration of students

    def test_no_student_submissions(self):
        """
        If no student submissions exist, the appropriate message should be displayed
        """
        StudentSubmission.objects.all().delete()
        CourseWork.objects.all().delete()
        response = self.client.get(reverse('studentsubmission-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No student submissions')


class CourseDetailViewTests(TestCase):
    #  - fields: {name: Current Trends and Projects in Computer Science
    #             section: CMSC 495 6338}
    fixtures = ['courses']

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


class CourseRosterTests(TestCase):

    fixtures = ['classroom', 'courses', 'coursework', 'studentsubmission',
                'user', 'coursestudent']

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/courses/1/roster/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('course-roster', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/courses/1/roster/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/coursestudent_list.html')

    def test_all_students_listed(self):
        response = self.client.get(reverse('course-roster', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['roster']) == CourseStudent.objects.filter(course_id=1).count())
        self.assertContains(response, response.context['roster'][0].student.last_name)
        self.assertContains(response, response.context['roster'][1].student.last_name)
