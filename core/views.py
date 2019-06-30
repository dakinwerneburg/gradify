from django.views import generic

from .models import Course, StudentSubmission, CourseWork, CourseStudent
from django.views.generic import TemplateView


class IndexPageView(TemplateView):
    template_name = 'core/index.html'


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
        # Get a list of all course work for this course, returns and empty array if none exits
        coursework = CourseWork.objects.filter(course_id=self.kwargs['pk']).order_by('dueDate')
        if not coursework:
            return []

        # Get a list of all student submissions
        submissions = StudentSubmission.objects.filter(coursework__course_id=self.kwargs['pk'])

        # Get a list of students in the course
        # TODO replace this with a query for the complete class roster and move above submissions.
        # Return [] if empty.
        students = set([s.student for s in submissions])

        return self.populate_gradebook(submissions, coursework, students)

    @staticmethod
    def populate_gradebook(submissions, coursework, students):
        # Gradebook only gets populated if there are both coursework and students
        if not coursework or not students:
            return []

        # Create hash tables for quick lookup
        coursework_lookup = {k.id: v for v, k in enumerate(coursework)}
        student_lookup = {k.id: v for v, k in enumerate(students)}

        # Initialize the gradebook array with a dictionary element for each student (row).
        # The submissions array is initialized to None for every assignment (column) in this course
        gradebook = [{'student': s,
                      'submissions': [None for _ in range(len(coursework))],
                      'points_earned': None,
                      'max_points': None,
                      'average_grade': None}
                     for s in students]

        # Build out the gradebook
        for submission in submissions:
            # Look up the row (student) and column (coursework) this submission belongs in
            row = student_lookup[submission.student_id]
            col = coursework_lookup[submission.coursework_id]

            # Enter the submission object into the proper location in the table
            gradebook[row]['submissions'][col] = submission

            # Update the total earned points and maximum possible points for the student
            # We only count points for submissions that have an assigned grade
            if submission.assignedGrade:
                if gradebook[row]['max_points']:
                    gradebook[row]['max_points'] += submission.coursework.max_points
                    gradebook[row]['points_earned'] += submission.assignedGrade
                else:
                    gradebook[row]['max_points'] = submission.coursework.max_points
                    gradebook[row]['points_earned'] = submission.assignedGrade

        # Calculate each student's average grade (must have at least one graded assignment)
        for entry in gradebook:
            if entry['max_points']:
                entry['average_grade'] = "{:.2%}".format(entry['points_earned'] / entry['max_points'])

        return gradebook

    def get_context_data(self, **kwargs):
        """
        Augment the context with a list of course work in the correct order
        """
        context = super().get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.filter(course_id=self.kwargs['pk']).order_by('dueDate')
        context['course'] = Course.objects.get(pk=self.kwargs['pk'])
        return context


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'core/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.filter(course=self.kwargs['pk']).order_by('dueDate')
        return context


class CourseRosterView(generic.TemplateView):
    template_name = "core/coursestudent_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(id=self.kwargs['pk'])
        roster = CourseStudent.objects.filter(course_id=self.kwargs['pk']).order_by(
            'student__last_name', 'student__first_name')
        context['roster'] = roster
        context['course'] = course
        return context


class CourseWorkDetailView(generic.DetailView):
    model = CourseWork
    context_object_name = 'assignment'
    template_name = 'core/coursework_detail.html'
    pk_url_kwarg = 'pk2'

    def get_context_data(self, **kwargs):
        # Provides access to Assignemnt and Course info for the entered course_id and coursework_id
        context = super().get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.get(pk=self.kwargs['pk2'])
        context['course'] = Course.objects.get(pk=self.kwargs['pk'])
        return context
