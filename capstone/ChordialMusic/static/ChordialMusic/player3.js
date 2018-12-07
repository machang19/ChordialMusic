var MidiPlayer2 = MidiPlayer;
var loadFile2, loadDataUri2, Player2;
var AudioContext = window.AudioContext || window.webkitAudioContext || false;
var ac = new AudioContext || new webkitAudioContext;
var eventsDiv = document.getElementById('events');
var bar_length = 0;
var o_tempo = 0; 

var changeTempo2 = function(tempo) {
    if (o_tempo == 0){
        o_tempo = Player2.tempo;
    }
    bar_length = (Player2.tempo/ temp ) * bar_length;
	Player2.tempo = tempo;
}

var play2 = function() {
	Player2.play();
	$('#play-button-chord2').children('img').attr('src', "/static/assets/pause.png");
}

var pause2 = function() {
	Player2.pause();
    $('#play-button-chord2').children('img').attr('src', "/static/assets/play.png");
}

var stop2 = function() {
	Player2.stop();
	$('#play-button-chord2').children('img').attr('src', "/static/assets/play.png");
}

var buildTracksHtml2 = function() {
	Player2.tracks.forEach(function(item, index) {
		var trackDiv = document.createElement('div');
		trackDiv.id = 'track-' + (index+1);
		var h5 = document.createElement('h5');
		h5.innerHTML = 'Track ' + (index+1);
		var code = document.createElement('code');
		trackDiv.appendChild(h5);
		trackDiv.appendChild(code);
		eventsDiv.appendChild(trackDiv);
	});
}

function getChordFile() {
    var id = document.getElementById("song_id2").value;
    console.log(id);
    $.ajax({
        url: "/chord",
        data: "song_id=" + id,
        success: loadDataUri2
    });
    var id = document.getElementById("song_id1").value;
    console.log(id);
    $.ajax({
        url: "/chord",
        data: "song_id=" + id,
        success: loadDataUri1
    });
    var id = document.getElementById("original_song_id").value;
    console.log(id);
    $.ajax({
        url: "/chord",
        data: "song_id=" + id,
        success: loadDataUri
    });
}

function generateChords() {

}

Soundfont.instrument(ac, 'https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/MusyngKite/acoustic_guitar_nylon-mp3.js').then(function (instrument) {
	document.getElementById('loading-chord2').style.display = 'none';
	document.getElementById('select-file').style.display = 'block';

    function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
    }

	loadFile2 = function() {
		var file    = document.forms['form2']['file2'].files[0];
		console.log(file)
		var reader  = new FileReader();
		console.log(getCSRFToken());
		if (file) reader.readAsArrayBuffer(file);

		reader.addEventListener("load", function () {
			Player2 = new MidiPlayer.Player(function(event) {
				if (event.name == 'Note on') {
					instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
					//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				}

				document.getElementById('tempo-display-chord2').innerHTML = Player2.tempo;
				document.getElementById('file-format-display-chord2').innerHTML = Player2.format;
				document.getElementById('play-bar-chord2').style.width = 100 - Player2.getSongPercentRemaining() + '%';
			});

			Player2.loadArrayBuffer(reader.result);

			document.getElementById('play-button-chord2').removeAttribute('disabled');

			//buildTracksHtml();
			play2();
		}, false);
	}





	loadDataUri2 = function(dataUri) {
        var chord_list = []
        var id = document.getElementById("song_pk2").value;
        console.log(id);
       var chord_list = []
        var length = 0;
        $.ajax({
            url: "/get_chords",
            data: "song_id=" + id,
            success: function(data) {
                console.log(data)
                chord_list = data.split(" ");
                console.log(chord_list)
                length = chord_list[chord_list.length-2];
                bar_length = chord_list[chord_list.length-1];
                console.log(length)
                console.log(bar_length)
                chord_list.splice(chord_list.length-2,2);
                console.log(chord_list)
                }
        });

		Player2 = new MidiPlayer.Player(function(event) {
			if (event.name == 'Note on' && event.velocity > 0) {
				instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
				//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				//console.log(event);
			}

			document.getElementById('tempo-display-chord2').innerHTML = Player2.tempo;
			document.getElementById('file-format-display-chord2').innerHTML = Player2.format;
			document.getElementById('play-bar-chord2').style.width = 100 - Player2.getSongPercentRemaining() + '%';


            var num_display = 9;
            var current_time = Player2.getSongTime() - Player2.getSongTimeRemaining();
            var interval = 100 / length;
            var current_index = Math.floor(current_time/(bar_length/1000));
            var start_index = 0
            var end_index = chord_list.length-1;
            var half_num = (num_display-1)/2
            var color_style = ""
            var output = ""

            if (current_index > half_num) {
                start_index = current_index - half_num;
            }
            if (current_index < (chord_list.length-half_num )) {
                end_index = current_index + half_num
            }
            for (i = start_index; i < end_index + 1; i++) {
                opacity = 1- Math.abs(i - current_index) / half_num;
                if (i == current_index) {
                    color_style = "; color: #F1A35A;"
                } else {
                    color_style = ""
                }
                output = output + "<span style='opacity: " + opacity + color_style +"'>" + chord_list[i] + "</span>" + "\t"
            }

            $('#generated_chords_2').html(output)


		});
		console.log(dataUri);
		Player2.loadDataUri(dataUri);
		if (o_tempo != 0){
            bar_length = (o_tempo/Player2.tempo) * bar_length
        }

		document.getElementById('play-button-chord2').removeAttribute('disabled');

		//buildTracksHtml();
		//play2();
	}




});