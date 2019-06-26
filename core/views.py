from django.views import generic
from django.shortcuts import get_object_or_404, render
from .models import Course, StudentSubmission, CourseWork, CourseStudent


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

        # Get a list of all course work for this course
        # TODO sort by dueDate instead
        coursework = CourseWork.objects.filter(course_id=1).order_by('created')

        # Get a list of students in the course
        # TODO replace this with a query for the complete class roster
        students = set([s.student for s in submissions])

        # Create hash tables for quick lookup
        coursework_lookup = {k.id: v for v, k in enumerate(coursework)}
        student_lookup = {k.id: v for v, k in enumerate(students)}

        # Initialize the gradebook array with a dictionary element for each student (row).
        # The submissions array is initialized to None for every assignment (column) in this course
        gradebook = [{'student': s, 'submissions': [None for _ in range(len(coursework))]}
                     for s in students]

        # Populate the gradebook
        for submission in submissions:
            # Look up the row (student) and column (coursework) this submission belongs in
            row = student_lookup[submission.student_id]
            col = coursework_lookup[submission.coursework_id]

            # Enter the submission object into the proper location
            gradebook[row]['submissions'][col] = submission

        return gradebook

    def get_context_data(self, **kwargs):
        """
        Augment the context with a list of course work in the correct order
        """
        context = super().get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.filter(course_id=1)
        return context


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'core/course_detail.html'


def view_course_roster(request, pk):
    course = Course.objects.get(id=pk)
    roster = CourseStudent.objects.filter(course_id=pk).order_by('student__last_name', 'student__first_name')

    context = {
        'roster': roster,
        'course': course,
    }

    return render(request, "core/coursestudent_list.html", context)
