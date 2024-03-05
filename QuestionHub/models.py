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
    total_views = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    
class Topic(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
class Post(models.Model):
    author = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=False)
    body = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    num_views = models.IntegerField(default=0)
    
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

class Vote(models.Model):
    VOTE_CHOICES = (
        ('U', 'Upvote'),
        ('D', 'Downvote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Response, on_delete=models.CASCADE, null=True, blank=True)
    vote_type = models.CharField(max_length=1, choices=VOTE_CHOICES)

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

    def __str__(self):
        if self.post:
            return f'{self.user.username} - {self.post.title} - {self.get_vote_type_display()}'
        elif self.comment:
            return f'{self.user.username} - {self.comment.text} - {self.get_vote_type_display()}'

Vote._meta.unique_together = (('user', 'post'), ('user', 'comment'))