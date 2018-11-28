from django.db import models

# Create your models here.

class ChordProgression(models.Model):
    song_name = models.TextField(max_length=200)
    chords = models.TextField(max_length=600)
