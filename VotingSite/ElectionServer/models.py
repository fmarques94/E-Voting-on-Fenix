from django.db import models
from django.contrib.auth.models import AbstractUser

class FenixUser(AbstractUser):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=100)