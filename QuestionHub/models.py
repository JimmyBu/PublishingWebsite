from django.db import models
"""
class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    num_posts = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    karma = models.IntegerField(default=0)
"""
class Topic(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    topic_name = models.CharField(max_length=255)

class Post(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    #author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete = models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

class Comment(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
   # author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=False, blank=True, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_nested_comment = models.BooleanField(default=False)
    comment_number = models.IntegerField(default=0)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

