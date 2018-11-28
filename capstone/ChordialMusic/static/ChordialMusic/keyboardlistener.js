// Create a MIDI file. Type 1; 100 clocks per quarter note.
// Normally, it would rather be 96, but 100 makes it easier to count.
tpqn = 96;
var smf = new JZZ.MIDI.SMF(0, tpqn);
bpm = 90;
var first = true;
// Add MIDI file tracks:
var trk0 = new JZZ.MIDI.SMF.MTrk(); smf.push(trk0); // First track in Type 1 MIDI file is normally used for tempo changes
trk0.smfSeqName('Little Lame') // The name of the first track serves as the file title
    .smfBPM(bpm) // Tempo. Normally set at clock 0, but can be also changed later
    .ch(0) // all subsequent messahes will go to channel 0
    .program(0x0b); // set channel 0 program to vibraphone
     // otherwise it will end on clock 1690


navigator.requestMIDIAccess()
    .then(onMIDISuccess, onMIDIFailure);


globalInput = null;
function onMIDISuccess(midiAccess) {
    for (var input of midiAccess.inputs.values()){

        input.onmidimessage = getMIDIMessage;
        input.onstatechange = printState;
        console.log(input)
        globalInput = input;

    }
}
function onMIDIFailure() {
    console.log('Could not access your MIDI devices.');
}

function printState() {
    console.log(globalInput.state)
}
start_time = 0;
recording = false;
 end_time = 0;

function startRecording(){
    recording = true;
}
function getMIDIMessage(message) {
    if (recording){
    var command = message.data[0];
    var note = message.data[1];
    var velocity = (message.data.length > 2) ? message.data[2] : 0; // a velocity value might not be included with a noteOff command

    switch (command) {
        case 144: // noteOn
            console.log(message)
            if (first) {
                start_time = message.timeStamp;
                trk0.add(0, JZZ.MIDI.noteOn(0, note, velocity));
                console.log(0)
                first = false;

            } else {
                new_time = message.timeStamp;
                ticks = (new_time - start_time)/(60000) *  bpm * tpqn;
                console.log(ticks);
                trk0.add(ticks,JZZ.MIDI.noteOn(0, note, velocity));
            }
            break;
        case 128: // noteOff
            console.log(message);
            new_time = message.timeStamp;
            end_time = new_time;
            ticks = (new_time - start_time)/(60000) * bpm * tpqn;
            console.log(ticks);
            trk0.add(ticks,JZZ.MIDI.noteOff(0, note, velocity));
            break;
        // we could easily expand this switch statement to cover other types of commands such as controllers or sysex
    }}
}

function stopRecording() {
    ticks = end_time/(60000) * bpm * tpqn;
    console.log(ticks);
    trk0.add(ticks, JZZ.MIDI.smfEndOfTrack());
    var str = smf.dump(); // MIDI file dumped as a string
    var b64 = JZZ.lib.toBase64(str); // convert to base-64 string
    var uri = 'data:audio/midi;base64,' + b64; // data URI

// Finally, write it to the document as a link and as an embedded object:
    document.getElementById('out').innerHTML = 'New file: <a download=lame.mid href=' + uri + '>DOWNLOAD</a> <embed src=' + uri + ' autostart=false>';



}