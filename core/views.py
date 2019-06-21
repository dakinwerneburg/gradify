from django.views import generic

from .models import Course


class CoursesView(generic.ListView):
    template_name = 'core/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        # TODO use the ownerId of the currently logged on user
        return Course.objects.filter(ownerId='teacher@gmail.com')
