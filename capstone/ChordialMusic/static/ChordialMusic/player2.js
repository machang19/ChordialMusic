var MidiPlayer1 = MidiPlayer;
var loadFile1, loadDataUri1, Player1;
var AudioContext = window.AudioContext || window.webkitAudioContext || false;
var ac = new AudioContext || new webkitAudioContext;
var eventsDiv = document.getElementById('events');
var bar_length = 0;
var o_tempo = 0;


var changeTempo1 = function(tempo) {
    if (o_tempo == 0){
        o_tempo = Player1.tempo;
    }
    bar_length = (Player1.tempo/ tempo ) * bar_length;
	Player1.tempo = tempo;
}

var play1 = function() {
	Player1.play();
	$('#play-button-chord1').children('img').attr('src', "/static/assets/pause.png");
}

var pause1 = function() {
	Player1.pause();
    $('#play-button-chord1').children('img').attr('src', "/static/assets/play.png");
}

var stop1 = function() {
	Player1.stop();
	$('#play-button-chord1').children('img').attr('src', "/static/assets/play.png");
}

var buildTracksHtml1 = function() {
	Player1.tracks.forEach(function(item, index) {
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





Soundfont.instrument(ac, 'https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/MusyngKite/acoustic_guitar_nylon-mp3.js').then(function (instrument) {
	document.getElementById('loading-chord1').style.display = 'none';
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

	loadFile1 = function() {
		var file    = document.forms['form1']['file1'].files[0];
		console.log(file)
		var reader  = new FileReader();
		console.log(getCSRFToken());
		if (file) reader.readAsArrayBuffer(file);

		reader.addEventListener("load", function () {
			Player1 = new MidiPlayer.Player(function(event) {
				if (event.name == 'Note on') {
					instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
					//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				}
				document.getElementById('tempo-display-chord1').innerHTML = Player1.tempo;
				document.getElementById('file-format-display-chord1').innerHTML = Player1.format;
				document.getElementById('play-bar-chord1').style.width = 100 - Player1.getSongPercentRemaining() + '%';
			});

			Player1.loadArrayBuffer(reader.result);

			document.getElementById('play-button-chord1').removeAttribute('disabled');

			//buildTracksHtml();
			play1();
		}, false);
	}



	loadDataUri1 = function(dataUri) {
        var chord_list = [] 
        var id = document.getElementById("song_pk1").value;
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

		Player1 = new MidiPlayer.Player(function(event) {
			if (event.name == 'Note on' && event.velocity > 0) {
				instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
				//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				//console.log(event);
			}

			document.getElementById('tempo-display-chord1').innerHTML = Player1.tempo;
			document.getElementById('file-format-display-chord1').innerHTML = Player1.format;
			document.getElementById('play-bar-chord1').style.width = 100 - Player1.getSongPercentRemaining() + '%';

            console.log(length)

            var num_display = 9;
            var current_time = Player1.getSongTime() - Player1.getSongTimeRemaining();
            var interval = 100 / length;
            var current_index = Math.floor(current_time/(bar_length/1000));
            console.log(current_index);
            console.log(current_time);
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

            $('#generated_chords_1').html(output)


		});
		console.log(dataUri);
		Player1.loadDataUri(dataUri);
		if (o_tempo != 0){
            bar_length = (o_tempo/Player1.tempo) * bar_length
        }

		document.getElementById('play-button-chord1').removeAttribute('disabled');

		//buildTracksHtml();
		//play1();
	}




});

