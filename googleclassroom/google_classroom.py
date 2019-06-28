from users.models import CustomUser
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialToken
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
        coursework = coursework_results.get('courseWork', [])
        return coursework

    def get_course_submissions(self, request, course_id, course_work_id):
        service = self.get_service(request)
        submission_results = service.courses().courseWork().studentSubmissions()\
            .list(courseId=course_id, courseWorkId=course_work_id).execute()
        submissions = submission_results.get('studentSubmissions', [])
        return submissions

    def is_google_user(self, request):
        usr = request.user.id
        users = CustomUser.objects.filter(id=usr)

        if not users:
            return False

        user = CustomUser.objects.filter(id=usr).first()
        googleUser = SocialToken.objects.filter(account__user=user, account__provider='google')

        if not googleUser:
            return False
        else:
            return True
