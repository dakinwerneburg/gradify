from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    token = models.TextField(null=True)
    organization = models.CharField(null=True, max_length=128, blank=True)
