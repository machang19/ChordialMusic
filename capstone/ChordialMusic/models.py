from django.db import models

# Create your models here.

class ChordProgression(models.Model):
    songName = models.CharField(max_length=200)
    chords = models.CharField(max_length=600)
