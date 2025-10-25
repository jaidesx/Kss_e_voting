from django.db import models
from candidates.models import Candidate


class Voter(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    student_name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20)
    house = models.CharField(max_length=50)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return self.student_name

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'post')
