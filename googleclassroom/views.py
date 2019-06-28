from allauth.socialaccount.models import SocialAccount
from django.views import generic
from googleclassroom.google_classroom import ClassroomHelper
from django.http import HttpResponse
from django.urls import reverse


class CourseTestView(generic.ListView):
    template_name = 'google_classroom_list'

    def get(self, request):
        response = self.to_html(request)
        return HttpResponse(response)

    def to_html(self, request):
        ch = ClassroomHelper()
        if ch.is_google_user(request) is False:
            return "<span style='color:red'>You are NOT signed into Google!</span><br /><br />" \
                   "Please <a href='" + reverse('account_login') + "'>Sign In</a> with a Google Account"

        usr = request.user.id
        user_details = SocialAccount.objects.filter(user=usr).first()

        ret_table = "<table><tr><td><img style='width:50px;height:50px' src='" \
            + user_details.extra_data["picture"] + "'></td>"

        ret_table = ret_table + "<td>" + user_details.extra_data["name"] \
            + "<br /><a href='mailto:" + user_details.extra_data["email"] \
            + "'>" + user_details.extra_data["email"] \
            + "</td></tr></table>"

        ret_table = ret_table + "<h1>Courses</h1>"

        course = ch.get_courses(request)

        for course_detail in course:
            course_id = course_detail['id']
            course_name = course_detail['name']
            ret_table = ret_table + "<h2>" + course_name + " (" + course_id + ")</h2>"

            try:
                course_work = ch.get_course_works(request, course_id)
                for course_work_detail in course_work:
                    course_title = course_work_detail['title']
                    course_work_id = course_work_detail['id']
                    ret_table = ret_table + "<h3>" + course_title + "</h3>"

                    submission = ch.get_course_submissions(request, course_id, course_work_id)
                    if not submission:
                        ret_table = ret_table + "No Stduent Submissions Found<br />"
                    else:
                        for submission_detail in submission:
                            student_id = submission_detail['userId']
                            student_detail = ch.get_user_by_id(request, student_id)
                            student_name = student_detail["fullName"]
                            if 'assignedGrade' in submission_detail:
                                ret_table = ret_table \
                                    + "{0} ({1}) assignedGrade {2})<br />"\
                                    .format(student_name, student_id, submission_detail['assignedGrade'])
                            else:
                                ret_table = ret_table\
                                    + "{0} ({1}) assignedGrade (Not_Submitted)<br />".format(student_name, student_id)
            except Exception:
                ret_table = ret_table + "<span style='color:red'>No Permissions</span><br />"

        return ret_table
