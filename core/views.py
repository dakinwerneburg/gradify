from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenCredentialsError
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from core import gc_import_utils
from googleclassroom.google_classroom import ClassroomHelper
from users.models import CustomUser
from .models import Course, StudentSubmission, CourseWork, CourseStudent
from .forms import CourseWorkCreateForm
from .forms import CourseCreateForm

import logging

logger = logging.getLogger('gradify')


class IndexPageView(generic.TemplateView):
    template_name = 'core/index.html'


class CoursesView(LoginRequiredMixin, generic.ListView):
    """
    This view lists all courses associated with a Classroom.
    """
    template_name = 'core/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user_id = self.request.user.id
        return Course.objects.filter(Q(owner_id=user_id) | Q(coursestudent__student_id=user_id))


class StudentSubmissionsView(LoginRequiredMixin, generic.ListView):
    """
    This view represents the student submissions for a course.
    It is the gradebook overview for viewing all grades for a course.
    """
    template_name = 'core/studentsubmission_list.html'
    context_object_name = 'gradebook'

    def get_queryset(self):
        # Get a list of Students in the course
        students = [s.student for s in CourseStudent.objects.filter(course_id=self.kwargs['pk'])]
        if not students:
            return []

        # Get a list of all course work for this course, returns and empty array if none exits
        coursework = CourseWork.objects.filter(course_id=self.kwargs['pk']).order_by('dueDate')
        if not coursework:
            return []

        # Get a list of all student submissions
        submissions = StudentSubmission.objects.filter(coursework__course_id=self.kwargs['pk'])

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
                    gradebook[row]['max_points'] += submission.coursework.maxPoints
                    gradebook[row]['points_earned'] += submission.assignedGrade
                else:
                    gradebook[row]['max_points'] = submission.coursework.maxPoints
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


class CourseDetailView(LoginRequiredMixin, generic.DetailView):
    model = Course
    template_name = 'core/course_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['coursework'] = CourseWork.objects.filter(course=self.kwargs['pk']).order_by('dueDate')
        return context


class CourseRosterView(LoginRequiredMixin, generic.TemplateView):
    template_name = "core/coursestudent_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(id=self.kwargs['pk'])
        roster = CourseStudent.objects.filter(course_id=self.kwargs['pk']).order_by(
            'student__last_name', 'student__first_name')
        context['roster'] = roster
        context['course'] = course
        return context


class CourseWorkDetailView(LoginRequiredMixin, generic.DetailView):
    model = CourseWork
    context_object_name = 'assignment'
    template_name = 'core/coursework_detail.html'
    pk_url_kwarg = 'pk2'

    def get_context_data(self, **kwargs):
        # Provides access to Assignment and Course info for the entered course_id and coursework_id
        context = super().get_context_data(**kwargs)
        author = self.request.user.pk
        ownerId = self.request.user.email
        context['coursework'] = get_object_or_404(
            CourseWork, course=self.kwargs['pk'], author=author, pk=self.kwargs['pk2']
        )
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'], ownerId=ownerId)
        return context


@login_required
def gc_ingest_and_redirect(request):
    gc = ClassroomHelper()

    if not gc.is_google_user(request):
        # TODO change google_classroom_list to an error page
        # Redirect to error page
        return redirect(reverse('google_classroom_list'))

    # Make necessary requests to Google API and save the data in the db
    try:
        gc_courses = gc.get_courses(request)
    except AccessTokenCredentialsError:
        return redirect(reverse('google_classroom_list'))

    current_user = CustomUser.objects.get(id=request.user.id)
    for course in gc_courses:
        # Save the course to the database
        saved_course = gc_import_utils.import_course(course, current_user)

        # Get the coursework for this course
        try:
            gc_coursework = gc.get_coursework(request, saved_course.id)
        except HttpError:
            # User does not have permission to get coursework for this course
            logger.debug('No permissions for coursework in %s' % saved_course)
            continue

        for assignment in gc_coursework:
            gc_import_utils.import_assignment(assignment, saved_course)

    return redirect(reverse('course-list'))


class CourseWorkCreateView(generic.CreateView):
    model = CourseWork
    form_class = CourseWorkCreateForm
    template_name = 'core/coursework_create.html'
    success_url = '/course/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        coursework = form.save(commit=False)
        coursework.source = 'G'
        coursework.author = self.request.user
        coursework.save()
        return super(CourseWorkCreateView, self).form_valid(form)


class CourseCreateView(LoginRequiredMixin, generic.CreateView):
    model = Course
    form_class = CourseCreateForm
    template_name = 'core/course_create.html'
    success_url = '/course/'

    def form_valid(self, form):
        course = form.save(commit=False)
        course.enrollmentCode = get_random_string(length=6)
        course.ownerId = self.request.user.email
        course.save()
        return super(CourseCreateView, self).form_valid(form)
