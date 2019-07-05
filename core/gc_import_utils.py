from logging import getLogger

from allauth.socialaccount.models import SocialAccount

from core.models import Course, CourseStudent
from users.models import CustomUser

logger = getLogger('gradify')


def import_course(course: dict, user: CustomUser):
    """
    Checks if the current user is the owner of the course or is just enrolled in it.
    If the user owns the course, the course gets created or updated.
    Otherwise, the user is added as a CourseStudent.

    Returns the imported/updated/enrolled course
    """
    users_google_id = SocialAccount.objects.get(user=user).uid
    if users_google_id == course['ownerId']:
        # User is course owner
        course['owner'] = user

        # Remove any fields we don't want
        course = filter_course_fields(course)

        # Check if the course id exists in the database. If so, it gets updated. If not, it gets created.
        updated_course, created = Course.objects.update_or_create(id=course['id'], defaults=course)
        if created:
            logger.info("Created new course owned by user %s: %s" % (user, updated_course))
        else:
            logger.info("Updated existing course owned by user %s: %s" % (user, updated_course))

        return updated_course
    else:
        try:
            # Add user as a student enrolled in the course
            existing_course = Course.objects.get(id=course['id'])
            enrolled_student, created = CourseStudent.objects.get_or_create(student=user, course=existing_course)
            if created:
                logger.info("Added new student %s to course %s" % (user, course['name']))
            else:
                logger.debug("No changes for student %s in course %s" % (user, course['name']))

            return enrolled_student.course
        except Course.DoesNotExist:
            # Current user is importing this course before the user that actually owns it
            # Create the course, but let the owner be set as the default.
            # If the true owner ever imports it, it will be updated.
            course = filter_course_fields(course)
            new_course = Course.objects.create(**course)
            logger.info("Student %s imported a course with no owner on Gradify: %s" % (user, new_course))

            # Add the user as an enrolled student
            CourseStudent.objects.create(student=user, course=new_course)
            logger.info("Added student %s to course %s" % (user, course['name']))

            return new_course


def filter_course_fields(course: dict):
    # Copy the course to a new var to prevent modifying the original
    filtered_course = dict(course)

    # Delete any attrs which may be present and are not needed

    for attr in ['teacherGroupEmail', 'courseGroupEmail', 'teacherFolder',
                 'courseMaterialSets', 'guardiansEnabled', 'calendarId']:
        try:
            del filtered_course[attr]
        except KeyError:
            continue

    return filtered_course
