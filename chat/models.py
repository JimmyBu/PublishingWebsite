from django.db import models
from django.contrib.auth.models import User
from QuestionHub.models import UserProfile


# TODO: Notification not finished
# TODO: Function to create profile
# TODO: Function to add friends
# TODO: Function restrict adding friends to self.
# TODO: Add friends Function should be bi-directional.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pic = models.ImageField(upload_to="img", blank=True, null=True)
    friends = models.ManyToManyField('Friend', related_name='my_friends', blank=True)

    def __str__(self):
        return self.name

    def add_friend(self, friend):
        self.friends.add(friend)

    def remove_friend(self, friend):
        self.friends.remove(friend)

    def get_friends(self):
        return self.friends.all()


class Friend(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="all_friends")

    @property
    def num_of_messages(self):
        chats = ChatMessage.objects.filter(msg_sender=self.profile, seen=False)
        return chats.count

    def __str__(self):
        return self.profile.name


class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="msg_receiver")
    seen = models.BooleanField(default=False)

    def __str__(self):
        return self.body
