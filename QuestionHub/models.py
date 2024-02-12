from django.db import models
from django.contrib.auth.models import User

# problem of comment, the null and blank on the post and comment side makes a controversial.
"""class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    num_posts = models.IntegerField(default=0)
    num_comments = models.IntegerField(default=0)
    karma = models.IntegerField(default=0)


class Topic(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    topic_name = models.CharField(max_length=255)


class Post(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    comment = models.TextField()


class Comment(models.Model):
    # is_nested_comment = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True, editable=False)
    comment_number = models.IntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE,
                                       related_name='child_comments')
    comment = models.TextField()
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)"""


class Post(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=False)
    body = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

    # define a readable title
    def __str__(self):
        return self.title

    def get_comment(self):
        return self.comments.filter(parent=None)  # parent=None retrieves all the first level comments


class Response(models.Model):
    post = models.ForeignKey(Post, null=False, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    body = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.body

    def get_comment(self):
        return Response.objects.filter(parent=self)  # retrieve all the replies


"""class UpVote(models.Model):
    vote = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upvote')


class DownVote(models.Model):
    vote = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downvote')
"""