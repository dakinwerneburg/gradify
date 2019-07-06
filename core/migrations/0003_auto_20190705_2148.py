# Generated by Django 2.2.1 on 2019-07-05 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190703_0412'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coursework',
            old_name='type',
            new_name='workType',
        ),
        migrations.AddField(
            model_name='coursework',
            name='alternateLink',
            field=models.TextField(blank=True, max_length=650),
        ),
        migrations.AddField(
            model_name='coursework',
            name='creationTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coursework',
            name='creatorUserId',
            field=models.CharField(default=1, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursework',
            name='updateTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]