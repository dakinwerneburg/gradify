from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    token = models.TextField(null=True)
    pass
