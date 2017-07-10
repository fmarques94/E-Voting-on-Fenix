import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

class FenixUser(AbstractUser):
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=100)

class Election(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.TextField()
    description = models.TextField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    openCastTime = models.TimeField()
    closeCastTime = models.TimeField()
    cryptoParameters = models.TextField()
    admin = models.ForeignKey(FenixUser, on_delete = models.CASCADE)
    publicKey = models.TextField()

class Trustee(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    id = models.TextField()
    name = models.TextField()
    email = models.EmailField(max_length=200)
    publicKeyShare = TextField()
    class Meta:
        unique_together = (('election','id'),)
    
class Voter(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    id = models.TextField()
    email = models.EmailField(max_length=200)
    publicCredential = models.TextField()
    class Meta:
        unique_together = (('election','id'),)

class Question(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    question = models.TextField()

class Answer(models.Model):
    question = models.ForeignKey(Question,on_delete = models.CASCADE)
    answer = TextField()

class Ballot(models.Model):
    election = models.ForeignKey(Question,on_delete = models.CASCADE)
    ballot = models.TextField()
    publicCredential = models.TextField()
    class Meta:
        unique_together = (('election','publicCredential'),)