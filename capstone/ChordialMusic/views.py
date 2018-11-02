
import mimetypes

import mingus
import numpy as np
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render
import mido
# Create your views here.
from django.utils.encoding import smart_str
from math import ceil
from mido import MidiFile, MidiTrack, Message
import os
from mlRun import predict


def handle_uploaded_file(f):
    with open(default_storage.path('tmp/'+f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    (result, channels, mid2, bar_length, num_bars) = parse_midi_file(default_storage.path('tmp/'+f.name))
    ml_arr = predict(np.array(result), num_bars)
    return output_to_midi(ml_arr, mid2, bar_length, channels)

class Note:
    def __init__(self, note, start, end):
        self.note = note
        self.start = start
        self.end = end
    def __str__(self):
        return ("Note note = %s start = % d end = % d length = %d" %(noteNumToString(self.note),self.start,self.end,self.end-self.start) )


def noteNumToindex(note_num):
    letters = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    noteIndex = ((note_num+3) % 12)
    return noteIndex

def noteNumToString(note_num):
    letters = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    noteIndex = ((note_num+3) % 12)
    note = letters[noteIndex] + str((note_num+3) // 12 - 1) 
    return note
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
            time += msg.time
            if not msg.is_meta:
                if (firstMessage):
                    firstMessage = False
                    for note in arr_to_chord(ml_arr[index]):
                        track.append(Message('note_on', channel=channel, note=note, time=0))
                    track.append(msg)
                    continue

            if (index < len(ml_arr)):
                if (time >= nextBarStart):
                    track.append(msg)
                    msgs_to_add = []
                    for note in arr_to_chord(ml_arr[index]):
                        msgs_to_add.append(Message('note_off',channel=channel, note=note, time=0))
                    index += 1
                    if (index < len(ml_arr)):
                        for note in arr_to_chord(ml_arr[index]):
                            msgs_to_add.append(Message('note_on', channel=channel, note=note, time = 0))
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
    stream1 = stream.Stream()
    bar_length = mid2.ticks_per_beat * numerator
    for i, track in enumerate(mid2.tracks):
        print('Track {}: {}'.format(i, track.name))
        print('starrrrt')
        for msg in track:
            print(msg)
            time += msg.time
            if (msg.type == 'time_signature'):
                print("gere")
                numerator = msg.numerator
                denominator = msg.denominator
            elif (msg.type == 'note_on' and msg.velocity > 0):
                channels.add(msg.channel)
                open_notes.append(Note(msg.note,time, time))
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                for index in range(len(open_notes)):
                    midi_note = open_notes[index]
                    if(midi_note.note == msg.note):
                            midi_end = ceil(time / (bar_length / 16)) * (bar_length / 16)
                            midi_note.end = midi_end
                            all_notes.append(midi_note)
                            open_notes.pop(index)
                            stringNote = noteNumToString(midi_note.note)
                            length = (midi_note.end - midi_note.start) / mid2.ticks_per_beat
                            note_to_insert = note.Note(stringNote)
                            note_to_insert.quarterLength = length
                            stream1.append(note_to_insert)
                            break

    print(analysis.discrete.analyzeStream(stream1, 'Krumhansl').tonicPitchNameWithCase)
    print(len(all_notes))
    result = []
    curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
    time = 0;
    curbarStart = 0;

    print(bar_length)
    for midi_note in all_notes:
        print(midi_note)
        index = noteNumToindex(midi_note.note)
        time = midi_note.start
        if time >= (curbarStart + bar_length):
            curbarStart += bar_length
            temp = curbar
            result.append(temp)
            curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
        curbar[index] += (midi_note.end - midi_note.start)
    result.append(curbar)
    count = 0
    print(numerator)
    print(denominator)
    for x in result:
        correctionFactor =  16/bar_length
        for i in range(len(x)):
            x[i] = x[i] * correctionFactor
        print(x)
    print(" ")
    window = 4
    fourbar_result = []
    for i in range(0, len(result) - window + 1, 2):
        fourbar_result.append(result[i:i+window])
        #print(result[i:i+window])
    print(fourbar_result)
    return (fourbar_result,channels,mid2, bar_length, len(result))



parse_midi_file(r'C:\Users\Michael Chang\ChordialMusic\capstone\ChordialMusic\templates\midi\right3.mid')

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



