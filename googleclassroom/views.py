from allauth.socialaccount.models import SocialAccount
from django.views.generic.base import TemplateView
from googleclassroom.google_classroom import ClassroomHelper


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
