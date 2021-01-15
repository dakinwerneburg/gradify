# Generated by Django 2.2.1 on 2019-07-13 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190712_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='alternateLink',
            field=models.CharField(blank=True, max_length=650, verbose_name='Link'),
        ),
        migrations.AlterField(
            model_name='course',
            name='courseState',
            field=models.CharField(choices=[('COURSE_STATE_UNSPECIFIED', 'Unspecified'), ('ACTIVE', 'Active'), ('ARCHIVED', 'Archived'), ('PROVISIONED', 'Provisioned'), ('DECLINED', 'Declined'), ('SUSPENDED', 'Suspended')], default='COURSE_STATE_UNSPECIFIED', max_length=64),
        ),
        migrations.AlterField(
            model_name='course',
            name='descriptionHeading',
            field=models.CharField(blank=True, max_length=3600, verbose_name='Heading'),
        ),
        migrations.AlterField(
            model_name='course',
            name='endDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='course',
            name='startDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='coursework',
            name='dueDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='coursework',
            name='maxPoints',
            field=models.IntegerField(blank=True, verbose_name='Max Points'),
        ),
        migrations.AlterField(
            model_name='coursework',
            name='state',
            field=models.CharField(choices=[('COURSE_WORK_STATE_UNSPECIFIED', 'Unspecified'), ('PUBLISHED', 'Published'), ('DRAFT', 'Draft'), ('DELETED', 'Deleted')], default='COURSE_WORK_STATE_UNSPECIFIED', max_length=64),
        ),
        migrations.AlterField(
            model_name='coursework',
            name='workType',
            field=models.CharField(choices=[('COURSE_WORK_TYPE_UNSPECIFIED', 'Unspecified'), ('ASSIGNMENT', 'Assignment'), ('SHORT_ANSWER_QUESTION', 'Short Answer Question'), ('MULTIPLE_CHOICE_QUESTION', 'Multiple Choice Question')], default='COURSE_WORK_TYPE_UNSPECIFIED', max_length=64, verbose_name='Work Type'),
        ),
        migrations.AlterField(
            model_name='studentsubmission',
            name='courseWorkType',
            field=models.CharField(choices=[('COURSE_WORK_TYPE_UNSPECIFIED', 'Unspecified'), ('ASSIGNMENT', 'Assignment'), ('SHORT_ANSWER_QUESTION', 'Short Answer Question'), ('MULTIPLE_CHOICE_QUESTION', 'Multiple Choice Question')], default='COURSE_WORK_TYPE_UNSPECIFIED', max_length=64),
        ),
        migrations.AlterField(
            model_name='studentsubmission',
            name='state',
            field=models.CharField(choices=[('SUBMISSION_STATE_UNSPECIFIED', 'Unspecified'), ('NEW', 'New'), ('CREATED', 'Created'), ('TURNED_IN', 'Turned In'), ('RETURNED', 'Returned'), ('RECLAIMED_BY_STUDENT', 'Reclaimed by Student')], default='SUBMISSION_STATE_UNSPECIFIED', max_length=64),
        ),
    ]