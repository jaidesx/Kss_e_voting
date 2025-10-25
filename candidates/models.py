
from django.db import models
from posts.models import Post


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='candidates')
    _class = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='candidates/photos/', blank=True)
    stream = models.CharField(max_length=50, blank=True)
    slogan = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.post.title}"
