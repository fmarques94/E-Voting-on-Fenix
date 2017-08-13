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
    openCastTime = models.TimeField(null=True)
    closeCastTime = models.TimeField(null=True)
    cryptoParameters = models.TextField()
    admin = models.ForeignKey(FenixUser, on_delete = models.CASCADE)
    publicKey = models.TextField()
    hybrid = models.BooleanField()
    aggregatedEncTally = models.TextField(null=True)
    tally = models.TextField(null=True)
    paperResults = models.TextField(null=True)

class Trustee(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    identifier = models.TextField()
    name = models.TextField()
    email = models.EmailField(max_length=200)
    publicKeyShare = models.TextField(null=True)
    partialDecryption = models.TextField(null=True)
    keyShareProofRandom = models.TextField(null=True)
    decryptionProofRandom = models.TextField(null=True)
    class Meta:
        unique_together = (('election','identifier'),)
    
class Voter(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    identifier = models.TextField()
    email = models.EmailField(max_length=200)
    publicCredential = models.TextField()
    proofRandomValues = models.TextField(null=True)
    paperVoter = models.BooleanField(default=False)
    class Meta:
        unique_together = (('election','identifier'),)

class Question(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    question = models.TextField()
    class Meta:
        unique_together = (('election','question'),)

class Answer(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    question = models.ForeignKey(Question,on_delete = models.CASCADE)
    answer = models.TextField()
    class Meta:
        unique_together = (('question','answer'),)

class Ballot(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    ballot = models.TextField()
    publicCredential = models.TextField()
    SBT = models.TextField()        #SBT = smart Ballot Tracker
    class Meta:
        unique_together = (('election','publicCredential'),)