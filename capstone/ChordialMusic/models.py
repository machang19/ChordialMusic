from django.db import models

# Create your models here.

class ChordProgression(models.Model):
    songName = models.CharField()
    chords = models.CharField()
