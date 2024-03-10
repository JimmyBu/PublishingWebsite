# Generated by Django 4.2.11 on 2024-03-08 13:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('QuestionHub', '0014_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='num_views',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(blank=True, related_name='my_friends', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='pic',
            field=models.ImageField(blank=True, null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_views',
            field=models.IntegerField(default=0),
        ),
    ]