from django.test import TestCase

from core.views import StudentSubmissionsView
from core.tests.mocks import MockCoursework, MockSubmission, MockUser


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
