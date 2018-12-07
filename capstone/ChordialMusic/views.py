import mimetypes

import numpy as np
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from datauri import DataURI
import mido
from music21 import *
from django.utils.encoding import smart_str
from math import ceil
from mido import MidiFile, MidiTrack, Message
import os
#from mlRun import predict

import keras.models
import numpy as np

from ChordialMusic.models import ChordProgression

model_path = "ChordialMusic/mlModels/b128_e50_lstm64_0.3_0.3x2"
model = keras.models.load_model(model_path)
model._make_predict_function()

model_path2 = "ChordialMusic/mlModels/all_data_b128_e50_lstm64_0.3_0.3x2"
model2 = keras.models.load_model(model_path2)
model2._make_predict_function()

window = 4
Chords = {0: 'A', 1: 'A#', 2: 'B', 3: 'C', 4: 'C#', 5: 'D', 6: 'D#', 7: 'E', 8: 'F', 9: 'F#', 10: 'G', 11: 'G#', 12: 'Am', 13: 'A#m', 14: 'Bm', 15: 'Cm', 16: 'C#m', 17: 'Dm', 18: 'D#m', 19: 'Em', 20: 'Fm', 21: 'F#m', 22: 'Gm', 23: 'G#m'}
ChordToNote = {
    'A':   [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
    'A#':  [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'B':   [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'C':   [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
    'C#':  [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    'D':   [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    'D#':  [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
    'E':   [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    'F':   [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    'F#':  [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    'G':   [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    'G#':  [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    'Am':  [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    'A#m': [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'Bm':  [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],
    'Cm':  [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
    'C#m': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
    'Dm':  [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    'D#m': [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
    'Em':  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
    'Fm':  [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1],
    'F#m': [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
    'Gm':  [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    'G#m': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]
}

def transform(i, key_fifth):
    if i < 12:
        return (i - 5*key_fifth) % 12
    else:
        return (((i - 12) - 5*key_fifth) % 12) + 12

def predict(inp, numBars, key_fifth):
    res = []
    chords = []
    second = []
    print(inp.shape)
    pred = model.predict(inp)
    for x in range(0, numBars):
        argmax = np.argmax(pred[x], axis = 1)
        for i, arg in enumerate(argmax):
            arg2 = pred[x][i].argsort()[-2]
            if (x % 2 == 0):
                res.append(ChordToNote[Chords[transform(arg, key_fifth)]])
                chords.append(Chords[transform(arg, key_fifth)])
                second.append(Chords[transform(arg2, key_fifth)])
    print(chords)
    print(second)
    return res, chords

def predict2(inp, numBars, key_fifth):
    res = []
    chords = []
    second = []
    # print(list(inp))
    pred = model2.predict(inp)
    for x in range(0, numBars):
        argmax = np.argmax(pred[x], axis = 1)
        for i, arg in enumerate(argmax):
            arg2 = pred[x][i].argsort()[-2]
            if (x % 2 == 0):
                res.append(ChordToNote[Chords[transform(arg, key_fifth)]])
                chords.append(Chords[transform(arg, key_fifth)])
                second.append(Chords[transform(arg2, key_fifth)])
    print(chords)
    print(second)
    return res, chords

def handle_uploaded_file(request):
    f = request.FILES["file"]
    with open(default_storage.path('tmp/'+f.name), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    (result, channels, mid2, bar_length, num_bars, key_fifth) = parse_midi_file(default_storage.path('tmp/'+f.name))
    ml_arr,chords = predict(np.array(result), len(result), key_fifth)
    ml_arr2, chords2 = predict2(np.array(result), len(result), key_fifth)
    #ml_arr,chords = ([[1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],[0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],[1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],[0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]], ["A","A#", "A", "A#"])
    f_name = output_to_midi(ml_arr2, mid2, bar_length, channels, "chords1_" + f.name)
    f_name2 = output_to_midi(ml_arr, mid2, bar_length, channels, "chords2_" + f.name)
    str_chords = ""
    for c in chords:
        str_chords += c + " "
    print (f.name)
    print (str_chords)
    model = ChordProgression(song_name = f.name, chords = str_chords)
    model.save()
    str_chords = ""
    for c in chords2:
        str_chords += c + " "
    print (f.name)
    print (str_chords)
    model2 = ChordProgression(song_name = f.name, chords = str_chords)
    model2.save()
    return render(request, 'upload.html', {"id1": f_name, "o_id": f.name, "pk1": model.pk, "id2": f_name2, "pk2": model2.pk})

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


def get_file(request):
    file_name = request.GET["song_id"]
    file_full_path = default_storage.path('tmp/' + file_name)
    with open(file_full_path, 'rb+') as f:
        data = f.read()
    dataURI = DataURI.from_file(file_full_path)
    return HttpResponse(dataURI)

def download_file(request):
    file_name = request.GET["song_id"]
    file_full_path = default_storage.path('tmp/' + file_name)

    with open(file_full_path, 'rb+') as f:
        data = f.read()
    response = HttpResponse(data, content_type=mimetypes.guess_type(file_full_path)[0])
    response['Content-Disposition'] = "attachment; filename={0}".format(file_name)
    response['Content-Length'] = os.path.getsize(file_full_path)
    return response

def arr_to_chord(arr):
    result = []
    for i in range(len(arr)):
        if arr[i] > 0:
            result.append(57 + i)
    return result

def output_to_midi(ml_arr, mid, barlength, channels, file_name):
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
    for i, t in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in t:
            old_time = time
            time += msg.time
            if not msg.is_meta:
                if (firstMessage):
                    firstMessage = False
                    for note in arr_to_chord(ml_arr[index]):
                        track.append(Message('note_on', channel=channel, note=note, time=0))
                    track.append(msg)
                    continue

            # if (index < len(ml_arr)):
            while (time >= nextBarStart and index < len(ml_arr)):

                msgs_to_add = []
                for note in arr_to_chord(ml_arr[index]):
                    msgs_to_add.append(Message('note_off',channel=channel, note=note, time=0))
                index += 1
                if (index < len(ml_arr)):
                    for note in arr_to_chord(ml_arr[index]):
                        msgs_to_add.append(Message('note_on', channel=channel, note=note, time = 0))
                if (nextBarStart - old_time >= 0 and nextBarStart - old_time < barlength):
                    msgs_to_add[0].time = nextBarStart - old_time
                else:
                    msgs_to_add[0].time = barlength
                for m in msgs_to_add:
                    track.append(m)
                
                msg.time = time - nextBarStart
                nextBarStart += barlength
            track.append(msg)
            # else:
            #     track.append(msg)

        m = track.pop(-1)
        for note in arr_to_chord(ml_arr[-1]):
            track.append(Message('note_off', channel=channel, note=note, time=0))
        track.append(m)
       

    output_file.save(default_storage.path('tmp/'+file_name))
    file_full_path = default_storage.path('tmp/'+file_name)
    return file_name

def get_chords(request):
    id = request.GET["song_id"]
    print(id)
    chords = get_object_or_404(ChordProgression, id=id)
    print(chords.chords)
    return HttpResponse(chords.chords)

def update_rating(request):
    id = request.GET["song_id"]
    print(id)
    chords = get_object_or_404(ChordProgression, id=id)
    rating = request.GET["rating"]
    chords.rating = (chords.rating * chords.count + rating)/(chords.count + 1)
    chords.count += 1
    chords.save()
    print(chords.chords)
    return HttpResponse(chords.chords)

def parse_midi_file(filepath):
    mid2 = MidiFile(filepath)
    all_notes = []
    time = 0
    open_notes = []
    numerator = 4
    denominator = 4
    channels = set()
    stream1 = stream.Stream()
    bar_length = mid2.ticks_per_beat * numerator

    for i, track in enumerate(mid2.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            time += msg.time
            if (msg.type == 'time_signature'):
                numerator = msg.numerator
                denominator = msg.denominator
                bar_length = mid2.ticks_per_beat * numerator * 4 / denominator
            elif (msg.type == 'note_on' and msg.velocity > 0):
                channels.add(msg.channel)
                open_notes.append(Note(msg.note,time, time))
            elif (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)):
                for index in range(len(open_notes)):
                    midi_note = open_notes[index]
                    if(midi_note.note == msg.note):
                            ratio = numerator / denominator * 16
                            midi_end = ceil(time / (bar_length / ratio )) * (bar_length / ratio)
                            midi_note.end = midi_end
                            all_notes.append(midi_note)
                            open_notes.pop(index)
                            stringNote = noteNumToString(midi_note.note)
                            length = (midi_note.end - midi_note.start) / mid2.ticks_per_beat
                            note_to_insert = note.Note(stringNote)
                            note_to_insert.quarterLength = length
                            stream1.append(note_to_insert)
                            break
    print(mid2.ticks_per_beat)
    print(numerator)
    print(bar_length)
    key_fifth = analysis.discrete.analyzeStream(stream1, 'Krumhansl').sharps
    print(key_fifth)
    result = []
    curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
    time = 0;
    curbarStart = 0;

    carryover = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for midi_note in all_notes:
        print(midi_note)
        index = noteNumToindex(midi_note.note)
        time = midi_note.start
        while time >= (curbarStart + bar_length):
            curbarStart += bar_length
            temp = curbar
            result.append(temp)
            curbar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            curbar = [min(x, bar_length) for x in carryover]
            carryover = [max(0, x - bar_length) for x in carryover]
        if i == 0 and midi_note.end >= (curbarStart + bar_length):
            curbar[(index + 5*key_fifth) % 12] += (curbarStart + bar_length - midi_note.start)
            carryover[(index + 5*key_fifth) % 12] += (midi_note.end - (curbarStart + bar_length))
        else:
            curbar[(index + 5*key_fifth) % 12] += (midi_note.end - max(midi_note.start, curbarStart))
    result.append(curbar)

    # for midi_note in all_notes:
    #     index = noteNumToindex(midi_note.note)
    #     time = midi_note.start
    #     while time >= (curbarStart + bar_length):
    #         curbarStart += bar_length
    #         temp = curbar
    #         result.append(temp)
    #         curbar = [0,0,0,0,0,0,0,0,0,0,0,0]
    #     curbar[(index + 5*key_fifth) % 12] += (midi_note.end - midi_note.start)
    # result.append(curbar)
    count = 0
    
    for x in result:
        correctionFactor =  16/bar_length
        for i in range(len(x)):
            x[i] = x[i] * correctionFactor
    window = 4
    fourbar_result = []
    if (len(result) <= 3):
        fourbar_result = [result]
    else:
        for i in range(0, len(result) - window + 1, 2):
            fourbar_result.append(result[i:i+window])
    return (fourbar_result,channels,mid2, int(bar_length), len(result), key_fifth)


def parse_midi_file_with_chords(filepath):
    mid2 = MidiFile(filepath)
    all_notes = []
    time = 0
    open_notes = []
    numerator = 4
    denominator = 4
    channels = set()
    track1Result = []
    track2Result = []
    stream1 = stream.Stream()
    bar_length = mid2.ticks_per_beat * numerator
    for i, track in enumerate(mid2.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            time += msg.time
            if (msg.type == 'time_signature'):
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
                            # note_to_insert = note.Note(stringNote)
                            # note_to_insert.quarterLength = length
                            # stream1.append(note_to_insert)
                            break
        result = []
        curbar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        time = 0;
        curbarStart = 0;

        for midi_note in all_notes:
            index = noteNumToindex(midi_note.note)
            time = midi_note.start
            while time >= (curbarStart + bar_length):
                curbarStart += bar_length
                temp = curbar
                result.append(temp)
                curbar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            curbar[index] += (midi_note.end - midi_note.start)
        result.append(curbar)
        count = 0
        for x in result:
            correctionFactor = 16 / bar_length
            for i in range(len(x)):
                x[i] = x[i] * correctionFactor
        window = 4
        fourbar_result = []
        for i in range(0, len(result) - window + 1, 2):
            fourbar_result.append(result[i:i + window])
        if (len(track1Result) == 0 ): track1Result = fourbar_result
        else: track2Result = fourbar_result
        all_notes = []


    # print(analysis.discrete.analyzeStream(stream1, 'Krumhansl').tonicPitchNameWithCase)

    return (track1Result,track2Result,channels,mid2, bar_length, len(result))


# parse_midi_file(r'C:\Users\Michael Chang\ChordialMusic\capstone\ChordialMusic\templates\midi\right3.mid')
def get_temp_file_path(request):
    f = request.GET["file"]
    name = request.GET["name"]
    print(name)
    print(f)
    with open(default_storage.path('tmp/'+name), 'wb+') as destination:
        destination.write(f.encode())
    return HttpResponse()

def upload_file(request):
    print(request.POST)
    print(request.FILES)
    result = []
    if 'file' in request.FILES:
        return handle_uploaded_file(request)

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
