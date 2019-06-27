from django.test import TestCase
from django.urls import reverse

from ..models import Course, CourseWork, StudentSubmission
from ..views import StudentSubmissionsView
from .mocks import MockCoursework, MockSubmission, MockUser


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
        response = self.client.get('/courses/1/gradebook/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/studentsubmission_list.html')

    def test_all_assignments_listed(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['coursework']) == CourseWork.objects.filter(course_id=1).count())
        self.assertContains(response, response.context['coursework'][0])
        self.assertContains(response, response.context['coursework'][1])

    def test_all_students_listed(self):
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        # TODO change to class roster size after class roster implementation
        self.assertTrue(len(response.context['gradebook']) == 3)
        self.assertContains(response, response.context['gradebook'][0]['student'])
        self.assertContains(response, response.context['gradebook'][1]['student'])

    def test_no_coursework(self):
        """
        If no coursework exists for the course, the appropriate message should be displayed
        """
        CourseWork.objects.all().delete()
        response = self.client.get(reverse('studentsubmission-list', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Assignments')


class GradebookPopulationTests(TestCase):
    """
    Tests that the gradebook is correctly populated when the submissions data is processed
    """

    def test_no_submissions(self):
        """
        If no assignments have been submitted, the gradebook should still be populated with the students and coursework
        """
        submissions = []
        coursework = [MockCoursework(i, 10) for i in range(10)]
        students = [MockUser(i) for i in range(5)]

        gradebook = StudentSubmissionsView.populate_gradebook(submissions, coursework, students)
        self.assertEqual(len(gradebook), len(students))

    def test_no_students(self):
        """
        If there are no students in a course, the gradebook should be an empty list. No students, no gradebook.
        Submissions are included just to ensure that if a bug causes this to happen, the code still behaves as expected
        """
        submissions = [MockSubmission(i, MockCoursework(i, i), i) for i in range(5)]
        coursework = [MockCoursework(i, 10) for i in range(10)]
        students = []

        gradebook = StudentSubmissionsView.populate_gradebook(submissions, coursework, students)
        self.assertEqual(len(gradebook), 0)

    def test_no_coursework(self):
        """
        No coursework, no gradebook
        Submissions are included just to ensure that if a bug causes this to happen, the code still behaves as expected
        """
        submissions = [MockSubmission(i, MockCoursework(i, i), i) for i in range(5)]
        students = [MockUser(i) for i in range(5)]
        coursework = []

        gradebook = StudentSubmissionsView.populate_gradebook(submissions, coursework, students)
        self.assertEqual(len(gradebook), 0)

    def test_populate_dict(self):
        """
        The gradebook should contain an array of dictionaries with the following fields:
        * student: User object
        * submissions: an array of size len(coursework) with Submission objects. Coursework without a Sub should be None
        * average_grade: student's average grade across the student's submitted assignments that have a grade assigned
        """
        coursework = [MockCoursework(i, 10) for i in range(5)]
        students = [MockUser(1), MockUser(2)]
        submissions = [
            # Student 1
            MockSubmission(students[0].id, coursework[0], assigned_grade=8),
            MockSubmission(students[0].id, coursework[1], assigned_grade=4),
            MockSubmission(students[0].id, coursework[2], assigned_grade=7),
            MockSubmission(students[0].id, coursework[3], assigned_grade=8),
            MockSubmission(students[0].id, coursework[4], assigned_grade=None),
            # Student 2
            MockSubmission(students[1].id, coursework[0], assigned_grade=4),
            MockSubmission(students[1].id, coursework[1], assigned_grade=None),
            MockSubmission(students[1].id, coursework[2], assigned_grade=None),
            MockSubmission(students[1].id, coursework[3], assigned_grade=6),
            MockSubmission(students[1].id, coursework[4], assigned_grade=9)
        ]

        student_one_expected_avg = (8 + 4 + 7 + 8) / 40
        student_two_expected_avg = (4 + 6 + 9) / 30

        gradebook = StudentSubmissionsView.populate_gradebook(submissions, coursework, students)
        student_one, student_two = gradebook

        self.assertEqual(student_one['student'], students[0])
        self.assertEqual(student_two['student'], students[1])

        self.assertEqual(len(student_one['submissions']), 5)
        self.assertEqual(len(student_two['submissions']), 5)

        self.assertEqual(student_one['average_grade'], "{:.2%}".format(student_one_expected_avg))
        self.assertEqual(student_two['average_grade'], "{:.2%}".format(student_two_expected_avg))

    def test_no_graded_assignments(self):
        """
        If no assignments have been graded, the average_grade should be None
        """
        coursework = [MockCoursework(i, 10) for i in range(2)]
        students = [MockUser(1)]
        submissions = [
            MockSubmission(students[0].id, coursework[0], assigned_grade=None),
            MockSubmission(students[0].id, coursework[1], assigned_grade=None)
        ]

        gradebook = StudentSubmissionsView.populate_gradebook(submissions, coursework, students)
        self.assertEqual(gradebook[0]['average_grade'], None)


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
