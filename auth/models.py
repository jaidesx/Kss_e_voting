from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Viewer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

