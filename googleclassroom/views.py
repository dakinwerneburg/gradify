from allauth.socialaccount.models import SocialAccount
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from oauth2client.client import AccessTokenCredentialsError

from core.models import Course
from googleclassroom.google_classroom import ClassroomHelper
from users.models import CustomUser


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
    new_courses = map(lambda c: Course.create_gc_course(c, owner=current_user), gc_courses)

    try:
        Course.objects.bulk_create(new_courses, batch_size=100)
    except IntegrityError:
        # TODO occurs when PK already exists. does it still create any new courses?
        pass

    return redirect(reverse('course-list'))


class CourseTestView(TemplateView):
    template_name = 'google_classroom_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        ch = ClassroomHelper()

        if ch.is_google_user(self.request) is False:
            context['message'] = 'You are NOT signed into Google! Please Sign In with a Google Account'
            context['name'] = ''
            context['email'] = ''
            context['picture'] = ''
            context['courses'] = ''
        else:
            context['message'] = ''

            usr = self.request.user.id
            user_details = SocialAccount.objects.filter(user=usr).first()

            context['name'] = user_details.extra_data["name"]
            context['email'] = user_details.extra_data["email"]
            context['picture'] = user_details.extra_data["picture"]

            context['courses'] = ch.get_courses(self.request)

        return context
