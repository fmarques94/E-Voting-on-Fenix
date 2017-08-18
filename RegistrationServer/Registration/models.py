from django.db import models

class Election(models.Model):
    id = models.UUIDField(primary_key=True)
    endDate = models.DateTimeField()

class Credential(models.Model):
    election = models.ForeignKey(Election,on_delete = models.CASCADE)
    credential = models.TextField()
    class Meta:
        unique_together = (('election','credential'),)
