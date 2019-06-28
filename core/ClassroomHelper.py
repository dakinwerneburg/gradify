from users.models import CustomUser
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.models import SocialAccount
from oauth2client.client import AccessTokenCredentials


class ClassroomHelper:

    def get_credential(self, request):
        usr = request.user.id
        user = CustomUser.objects.filter(id=usr).first()
        tokens = SocialToken.objects.filter(account__user=user, account__provider='google').first()
        token = tokens.token
        creds = AccessTokenCredentials(token, "django-oauth-classroom-test/1.0", None)
        return creds

    def get_service(self, request):
        creds = self.get_credential(request)
        service = build('classroom', 'v1', credentials=creds)
        return service

    def get_user_by_id(self, request, student_id):
        service = self.get_service(request)
        user_profile_results = service.userProfiles().get(userId=student_id).execute()
        user_profile = user_profile_results.get('name', [])
        return user_profile

    def get_courses(self, request):
        service = self.get_service(request)
        course_results = service.courses().list(pageSize=10).execute()
        courses = course_results.get('courses', [])
        return courses

    def get_course_works(self, request, course_id):
        service = self.get_service(request)
        coursework_results = service.courses().courseWork().list(courseId=course_id).execute()
        courseworks = coursework_results.get('courseWork', [])
        return courseworks

    def get_course_submissions(self, request, course_id, course_work_id):
        service = self.get_service(request)
        sumbission_results = service.courses().courseWork().studentSubmissions()\
            .list(courseId=course_id, courseWorkId=course_work_id).execute()
        submissions = sumbission_results.get('studentSubmissions', [])
        return submissions

    def to_html(self, request):
        usr = request.user.id
        user_details = SocialAccount.objects.filter(user=usr).first()

        ret_table = "<table><tr><td><img style='width:50px;height:50px' src='" \
            + user_details.extra_data["picture"] + "'></td>"

        ret_table = ret_table + "<td>" + user_details.extra_data["name"] \
            + "<br /><a href='mailto:" + user_details.extra_data["email"] \
            + "'>" + user_details.extra_data["email"] \
            + "</td></tr></table>"

        ret_table = ret_table + "<h1>Courses</h1>"

        courses = self.get_courses(request)

        for course in courses:
            course_id = course['id']
            course_name = course['name']
            ret_table = ret_table + "<h2>" + course_name + " (" + course_id + ")</h2>"

            try:
                courseworks = self.get_course_works(request, course_id)
                for courseworks_detail in courseworks:
                    course_title = courseworks_detail['title']
                    course_work_id = courseworks_detail['id']
                    ret_table = ret_table + "<h3>" + course_title + "</h3>"

                    submissions = self.get_course_submissions(request, course_id, course_work_id)
                    if not submissions:
                        ret_table = ret_table + "No Stduent Submissions Found<br />"
                    else:
                        for submissions_detail in submissions:
                            student_id = submissions_detail['userId']
                            student_detail = self.get_user_by_id(request, course_id, student_id)
                            student_name = student_detail["fullName"]
                            if 'assignedGrade' in submissions_detail:
                                ret_table = ret_table \
                                    + "{0} ({1}) assignedGrade {2})<br />"\
                                    .format(student_name, student_id, submissions_detail['assignedGrade'])
                            else:
                                ret_table = ret_table\
                                    + "{0} ({1}) assignedGrade (Not_Submitted)<br />".format(student_name, student_id)
            except Exception:
                ret_table = ret_table + "<span style='color:red'>No Permissions</span><br />"

        return(ret_table)
