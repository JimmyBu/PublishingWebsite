#This module define user models that will be used by the website
#The custom model class name will be specified in setting.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Additional user info that are not related to authentication
    """
    id = models.AutoField(primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="")
    num_posts = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    karma = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username