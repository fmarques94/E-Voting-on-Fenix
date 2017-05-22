from django.db import models
from django.contrib.auth.models import AbstractUser

class FenixUser(AbstractUser):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=100)

class Election(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=400)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    timeOpenBooth = models.TimeField()
    timeCloseBooth = models.TimeField()
    admin = models.ForeignKey(FenixUser, on_delete = models.CASCADE)

class Question(models.Model):
    election = models.ForeignKey(Election,on_delete=models.CASCADE)
    question = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    answer = models.TextField()

class EligibleVoter(models.Model):
    election = models.ForeignKey(Election,on_delete=models.CASCADE)
    voterId = models.CharField(max_length=10)
    name = models.CharField(max_length=400)
    email = models.EmailField(max_length=100)
    paper = models.NullBooleanField()
    voted = models.BooleanField()
    class Meta:
        unique_together = (('election','voterId'),)
        
class Trustee(models.Model):
    election = models.ForeignKey(Election,on_delete=models.CASCADE)
    trusteeId = models.CharField(max_length=10)
    name = models.CharField(max_length=400)
    email = models.EmailField(max_length=100)
    class Meta:
        unique_together = (('election','trusteeId'),)