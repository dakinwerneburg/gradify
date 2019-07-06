from logging import getLogger

from allauth.socialaccount.models import SocialAccount

from core.models import Course, CourseStudent, CourseWork
from users.models import CustomUser

logger = getLogger('gradify')


def import_course(course: dict, user: CustomUser):
    """
    Checks if the current user is the owner of the course or is just enrolled in it.
    If the user owns the course, the course gets created or updated.
    Otherwise, the user is added as a CourseStudent.

    Returns the imported/updated/enrolled course
    """
    # Remove any fields we don't want
    course = filter_course_fields(course)
    users_google_id = SocialAccount.objects.get(user=user).uid
    if users_google_id == course['ownerId']:
        # User is course owner
        course['owner'] = user

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
            course_updated = Course.objects.filter(id=course['id']).update(**course) > 0
            existing_course = Course.objects.get(id=course['id'])
            if course_updated:
                logger.info('Updated course %s' % existing_course)

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
            new_course = Course.objects.create(**course)
            logger.info("Student %s imported a course with no owner on Gradify: %s" % (user, new_course))

            # Add the user as an enrolled student
            CourseStudent.objects.create(student=user, course=new_course)
            logger.info("Added student %s to course %s" % (user, course['name']))

            return new_course


def import_assignment(assignment: dict, course: Course):
    """
    Returns a CourseWork object which is created if it does not already exist
    """
    assignment = dict(assignment)
    assignment['course'] = course
    assignment['author'] = course.owner
    assignment['source'] = CourseWork.GOOGLE
    assignment['dueDate'] = assemble_due_date(assignment)

    filtered_assignment = filter_assignment_fields(assignment)

    saved_assignment, created = CourseWork.objects.update_or_create(id=filtered_assignment['id'],
                                                                    defaults=filtered_assignment)
    if created:
        logger.info('Saved new %s assignment: %s' % (course, saved_assignment))
    else:
        logger.debug('No changes to existing %s assignment: %s' % (course, saved_assignment))

    return saved_assignment


def import_student(student: dict, course: Course):
    """
    Gets or creates a user account associated with the student data from GC and saves/updates
    the user as a CourseStudent.
    """
    student_account = get_or_create_account(student)

    # Add student to the class roster
    enrollment, created = CourseStudent.objects.get_or_create(student=student_account, course=course)
    if created:
        logger.info('Enrolled student %s in %s' % (student_account, course))
    else:
        logger.debug('Student %s already enrolled in %s' % (student_account, course))

    return enrollment


def get_or_create_account(student: dict) -> CustomUser:
    """
    Given a student object from GC, returns the associated user account. if it exists.
    Otherwise, returns a newly created user account.
    """
    student_id = student['profile']['id']
    try:
        # Get the student's User instance via the student's google id
        student_account = SocialAccount.objects.get(uid=student_id).user
        logger.info('Found existing account for user %s' % student_account)
    except SocialAccount.DoesNotExist:
        # Create an oAuth account for the new student
        profile = student['profile']
        logger.debug(str(profile))
        acct_details = {
            'username': profile['emailAddress'],
            'email': profile['emailAddress'],
            'first_name': profile['name']['givenName'],
            'last_name': profile['name']['familyName'],
            'username': profile['emailAddress'],
        }

        student_account = CustomUser(**acct_details)
        student_account.set_unusable_password()
        student_account.save()

        # Create a SocialAccount for the new User
        SocialAccount.objects.create(uid=student_id, user=student_account, provider='google')

        logger.info('Created new account for user %s' % student_account)

    return student_account


def filter_course_fields(course: dict):
    filtered_attrs = ['teacherGroupEmail', 'courseGroupEmail', 'teacherFolder', 'courseMaterialSets',
                      'guardiansEnabled', 'calendarId']

    return filter_data(course, filtered_attrs)


def filter_assignment_fields(assignment: dict):
    filtered_attrs = ['courseId', 'materials', 'scheduledTime', 'associatedWithDeveloper', 'assigneeMode',
                      'individualStudentOptions', 'submissionModificationMode', 'topicId', 'assignment',
                      'multipleChoiceQuestion', 'dueTime']

    return filter_data(assignment, filtered_attrs)


def filter_data(data: dict, filtered_attrs):
    filtered_data = dict(data)
    for attr in filtered_attrs:
        try:
            del filtered_data[attr]
        except KeyError:
            continue
    return filtered_data


def assemble_due_date(assignment: dict):
    """
    Returns a timestamp string from the dueDate and dueTime dict attributes, if present.
    Returns None if there is no dueDate attribute.
    """
    try:
        date = assignment['dueDate']
    except KeyError:
        return None

    due_date = "%04d-%02d-%02d" % (date['year'], date['month'], date['day'])
    try:
        time = assignment['dueTime']
        due_date += " %02d:%02d:%02d.%03dZ" % (time['hours'], time['minutes'], time['seconds'], time['nanos'])
    except KeyError:
        # If no dueTime specified, default to the end of the day on the dueDate
        due_date += " 23:59:59.999Z"

    return due_date
