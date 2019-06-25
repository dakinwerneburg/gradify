from django.views import generic
from .models import Course, StudentSubmission, CourseWork


class CoursesView(generic.ListView):
    """
    This view lists all courses associated with a Classroom.
    """
    template_name = 'core/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        # TODO use the ownerId of the currently logged on user
        return Course.objects.filter(ownerId='teacher@gmail.com')


class StudentSubmissionsView(generic.ListView):
    """
    This view represents the student submissions for a course.
    It is the gradebook overview for viewing all grades for a course.
    """
    template_name = 'core/studentsubmission_list.html'
    context_object_name = 'gradebook'

    def get_queryset(self):
        # Get a list of all student submissions
        # TODO use the course currently being viewed
        submissions = StudentSubmission.objects.filter(coursework__course_id=1)

        # Get a list of all course work for this course, returns and empty array if none exits
        coursework = CourseWork.objects.filter(course_id=1).order_by('dueDate')
        if not coursework:
            return []

        # Get a list of students in the course
        # TODO replace this with a query for the complete class roster
        students = set([s.student for s in submissions])

        # Create hash tables for quick lookup
        coursework_lookup = {k.id: v for v, k in enumerate(coursework)}
        student_lookup = {k.id: v for v, k in enumerate(students)}

        # Initialize the gradebook array with a dictionary element for each student (row).
        # The submissions array is initialized to None for every assignment (column) in this course
        gradebook = [{'student': s, 'average_grade': None, 'submissions': [None for _ in range(len(coursework))]}
                     for s in students]

        # Populate the gradebook
        for submission in submissions:
            # Look up the row (student) and column (coursework) this submission belongs in
            row = student_lookup[submission.student_id]
            col = coursework_lookup[submission.coursework_id]

            # Enter the submission object into the proper location
            gradebook[row]['submissions'][col] = submission

        total_max = 0
        for assignment in coursework:
            total_max += assignment.max_points

        for student in gradebook:
            total_grade = 0
            for submission in student['submissions']:
                if submission:
                    total_grade += submission.assignedGrade
            student['average_grade'] = "{:.2%}".format(total_grade / total_max)

        return gradebook

    def get_context_data(self, **kwargs):
        """
        Augment the context with a list of course work in the correct order
        """
        context = super().get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.filter(course_id=1).order_by('dueDate')
        # TODO use the course currently being viewed
        context['course'] = Course.objects.get(pk=1)
        return context
