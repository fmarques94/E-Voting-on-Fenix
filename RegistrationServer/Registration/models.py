from django.db import models

class Election(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    p = models.TextField()
    q = models.TextField()
    g = models.TextField()

class EVoter(models.Model):
    election = models.ForeignKey(EVoter, on_delete = models.CASCADE)
    voterId = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    publicCredential = models.TextField()

    class Meta:
        unique_together = (('election','voterId'),)