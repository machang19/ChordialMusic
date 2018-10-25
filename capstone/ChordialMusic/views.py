import mingus
from django.shortcuts import render
import pygame
import mido
# Create your views here.
from mido import MidiFile
import os
from django.core.files.storage import default_storage



def handle_uploaded_file(f):
    with open(default_storage.path('tmp/'+f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    parse_midi_file(default_storage.path('tmp/'+f.name))
    os.remove(default_storage.path('tmp/'+f.name))
    return

class Note:
    def __init__(self, note, start, end):
        self.note = note
        self.start = start
        self.end = end
    def __str__(self):
        return ("Note note = %d start = % d end = % d length = %d" %(self.note,self.start,self.end,self.end-self.start) )


def int_to_index(note_num):
    letters = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    noteIndex = ((note_num+3) % 12)
    return noteIndex

def parse_midi_file(filepath):
    mid2 = MidiFile(filepath)
    all_notes = []
    time = 0
    open_notes = []
    print(mid2)
    numerator = 4
    denominator = 4

    for i, track in enumerate(mid2.tracks):
        print('Track {}: {}'.format(i, track.name))
        print('starrrrt')
        for msg in track:
            print(msg)
            if (msg.type == 'time_signature'):
                print("gere")
                numerator = msg.numerator
                denominator = msg.denominator
            elif (msg.type == 'note_on' and msg.velocity > 0):
                open_notes.append(Note(msg.note,time, time))
                time += msg.time
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                for index in range(len(open_notes)):
                    note = open_notes[index]
                    if(note.note == msg.note):
                        if (msg.time > 0):
                            note.end = time
                            all_notes.append(note)
                            open_notes.pop(index)
                            break
                time += msg.time
    print(len(all_notes))
    result = []
    curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
    time = 0;
    curbarStart = 0;
    bar_length = mid2.ticks_per_beat * numerator
    for note in all_notes:
        index = int_to_index(note.note)
        time = note.start
        if time > (curbarStart + bar_length):
            curbarStart += bar_length
            temp = curbar
            result.append(temp)
            curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
        curbar[index] += (note.end - note.start)
    for x in result:
        total = sum(x)
        if total > 0:
            correctionFactor = 16/total
        else:
            correctionFactor = 1
        for i in range(len(x)):
            x[i] = x[i] * correctionFactor
    return result




print(parse_midi_file(r'C:\Users\Michael Chang\machang17437\capstone\ChordialMusic\templates\midi\jinglebells.mid'))

def upload_file(request):
    print("here")
    print(request.POST)
    print(request.FILES)
    result = []
    if 'file' in request.FILES:
        handle_uploaded_file(request.FILES["file"])

        count = 0
        #print(file)
        i = 0
        # file_type = 0
        # num_tracks = 0
        # ticksPQN = 0
        # while (i < len(file)):
        #     b = file[i]
        #     if (b == 0x4d):
        #         b1 = file[i+1]
        #         b2 = file[i+2]
        #         b3 = file[i + 3]
        #         if (b1 == 0x54 and b2 == 0x68 and b3 == 0x64):




        #     print("{:02x}".format(b))
        # print(mido.parse(file))
        # for msg in mid:
        #     #print(msg)
        #
        #     assert(isinstance(msg,mido.Message))
        #     # if(msg.type == 'note_on'):
        #     #     print(msg.note)
    return render(request, 'upload.html', {})



