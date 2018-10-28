import mimetypes

import mingus
from django.http import HttpResponse
from django.shortcuts import render
import pygame
import mido
# Create your views here.
from django.utils.encoding import smart_str
from mido import MidiFile, MidiTrack, Message
import os
from django.core.files.storage import default_storage



def handle_uploaded_file(f):
    with open(default_storage.path('tmp/'+f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    (result, channels, mid2, bar_length) = parse_midi_file(default_storage.path('tmp/'+f.name))
    #os.remove(default_storage.path('tmp/'+f.name))
    return output_to_midi(ml_arr, mid2, bar_length, channels)

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
ml_arr = [[0,0,1,0,0,0,0,0,0,0,0,0,0], [0,1,0,0,0,0,1,0,0,1,0,0,0], [0,0,1,0,0,0,0,0,1,0,0,1,0], [0,1,0,0,0,0,0,0,0,0,0,1,0]]

def arr_to_chord(arr):
    result = []
    for i in range(len(arr)):
        if arr[i] > 0:
            result.append(57 + i)
    return result

def output_to_midi(ml_arr, mid, barlength, channels):
    channel = 0
    for i in range(15):
        if i not in channels:
            channel = i
            break
    time = 0
    index = 0
    output_file = MidiFile(type=0)
    track = MidiTrack()
    output_file.tracks.append(track)
    nextBarStart = barlength
    firstMessage = True
    output_file.ticks_per_beat = mid.ticks_per_beat
    print("ticks per beat")
    print(output_file.ticks_per_beat )
    for i, t in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        print('starrrrt')
        for msg in t:
            if not msg.is_meta:
                if (firstMessage):
                    firstMessage = False
                    for note in arr_to_chord(ml_arr[index]):
                        track.append(Message('note_on', channel=channel, note=note, time=0))
                    track.append(msg)
                    continue
            prevTime = time
            time += msg.time
            if (index < len(ml_arr)):
                if (time > nextBarStart):
                    msg.time = nextBarStart - prevTime
                    track.append(msg)
                    msgs_to_add = []
                    for note in arr_to_chord(ml_arr[index]):
                        msgs_to_add.append(Message('note_off',channel=channel, note=note, time=0))
                    index += 1
                    if (index < len(ml_arr)):
                        for note in arr_to_chord(ml_arr[index]):
                            msgs_to_add.append(Message('note_on', channel=channel, note=note, time = 0))
                    msgs_to_add[-1].time = time - nextBarStart
                    for m in msgs_to_add:
                        track.append(m)
                    nextBarStart += barlength
                else:
                    track.append(msg)
            else:
                track.append(msg)

    file_name = "test.mid"
    output_file.save(default_storage.path('tmp/'+file_name))
    file_full_path = default_storage.path('tmp/'+file_name)

    with open(file_full_path, 'rb+') as f:
        data = f.read()
    response = HttpResponse(data, content_type=mimetypes.guess_type(file_full_path)[0])
    response['Content-Disposition'] = "attachment; filename={0}".format(file_name)
    response['Content-Length'] = os.path.getsize(file_full_path)
    return response

def parse_midi_file(filepath):
    mid2 = MidiFile(filepath)
    all_notes = []
    time = 0
    open_notes = []
    print(mid2)
    numerator = 4
    denominator = 4
    channels = set()
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
                channels.add(msg.channel)
                open_notes.append(Note(msg.note,time, time))
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
        #print(note)
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
        #print(x)
    #print(channels)
    return (result,channels,mid2, bar_length)




parse_midi_file(r'C:\Users\Michael Chang\ChordialMusic\capstone\ChordialMusic\templates\midi\test (2).mid')

def upload_file(request):
    print("here")
    print(request.POST)
    print(request.FILES)
    result = []
    if 'file' in request.FILES:
        return handle_uploaded_file(request.FILES["file"])

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



