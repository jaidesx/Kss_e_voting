from django.db import models
from django.contrib.auth import get_user_model
from candidates.models import Candidate


User = get_user_model()


class Voter(models.Model):
    voter_no = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    house = models.CharField(max_length=50)
    has_voted = models.BooleanField(default=False)

    @property
    def is_authenticated(self):
        return True
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'post')
