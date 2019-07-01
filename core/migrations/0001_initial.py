# Generated by Django 2.2.1 on 2019-07-01 01:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=750)),
                ('enrollmentCode', models.CharField(max_length=64)),
                ('section', models.CharField(blank=True, max_length=2800)),
                ('descriptionHeading', models.CharField(blank=True, max_length=3600)),
                ('description', models.TextField(blank=True, max_length=30000)),
                ('room', models.CharField(blank=True, max_length=650)),
                ('alternateLink', models.CharField(blank=True, max_length=650)),
                ('startDate', models.DateTimeField(blank=True, null=True)),
                ('endDate', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('creationTime', models.DateTimeField(blank=True, null=True)),
                ('updateTime', models.DateTimeField(blank=True, null=True)),
                ('ownerId', models.CharField(max_length=254)),
                ('courseState', models.CharField(choices=[('U', 'Unspecified'), ('A', 'Active'), ('R', 'Archived'), ('S', 'Suspended')], default='U', max_length=1)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=750)),
                ('description', models.TextField(blank=True, max_length=30000)),
                ('max_points', models.IntegerField(blank=True)),
                ('dueDate', models.DateField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('U', 'Unspecified'), ('P', 'Published'), ('D', 'Draft'), ('X', 'Deleted')], default='U', max_length=1)),
                ('type', models.CharField(choices=[('U', 'Unspecified'), ('Q', 'Quiz'), ('T', 'Test'), ('W', 'Worksheet'), ('F', 'Final')], default='U', max_length=1)),
                ('source', models.CharField(choices=[('U', 'Unspecified'), ('C', 'Google Classroom'), ('G', 'Gradify')], default='U', max_length=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Course')),
            ],
        ),
        migrations.CreateModel(
            name='StudentSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('late', models.BooleanField(default=False)),
                ('draftGrade', models.FloatField(blank=True)),
                ('assignedGrade', models.FloatField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('U', 'Unspecified'), ('N', 'New'), ('C', 'Created'), ('T', 'Turned In'), ('R', 'Returned'), ('S', 'Reclaimed by Student')], default='U', max_length=1)),
                ('coursework', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.CourseWork')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CourseStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('classroomId', models.CharField(max_length=750, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=750)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
