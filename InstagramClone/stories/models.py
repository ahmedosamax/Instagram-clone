from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='story_images/')
    caption = models.CharField(max_length=2200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_expired = models.BooleanField(default=False) 

    def has_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)

    def viewers_count(self):
        return self.views.count()

    def __str__(self):
        return f"{self.user.username}'s Story"

class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'viewer')

    def __str__(self):
        return f"{self.viewer.username} viewed {self.story.user.username}'s story"
