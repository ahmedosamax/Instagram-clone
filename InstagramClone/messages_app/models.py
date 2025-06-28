from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Thread(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-created_at']

    def __str__(self):
        return f"Thread between {self.user1.username} and {self.user2.username}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} at {self.timestamp}"

