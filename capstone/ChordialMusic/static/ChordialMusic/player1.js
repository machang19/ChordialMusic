var MidiPlayer = MidiPlayer;
var loadFile, loadDataUri, Player;
var AudioContext = window.AudioContext || window.webkitAudioContext || false;
var ac = new AudioContext || new webkitAudioContext;
var eventsDiv = document.getElementById('events');


var changeTempo = function(tempo) {
	Player.tempo = tempo;
}

var play = function() {
	Player.play();
	$('#play-button').children('img').attr('src', "/static/assets/pause.png");
}

var pause = function() {
	Player.pause();
	$('#play-button').children('img').attr('src', "/static/assets/play.png");
}

var stop = function() {
	Player.stop();
	$('#play-button').children('img').attr('src', "/static/assets/play.png");

}

var buildTracksHtml = function() {
	Player.tracks.forEach(function(item, index) {
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
	document.getElementById('loading').style.display = 'none';
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

	loadFile = function() {
		var file    = document.querySelector('input[type=file]').files[0];
		console.log(typeof(file))
		var reader  = new FileReader();
		console.log(getCSRFToken());
		if (file) reader.readAsArrayBuffer(file);

		reader.addEventListener("load", function () {
			Player = new MidiPlayer.Player(function(event) {
				if (event.name == 'Note on') {
					instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
					//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				}

				document.getElementById('tempo-display').innerHTML = Player.tempo;
				document.getElementById('file-format-display').innerHTML = Player.format;
				document.getElementById('play-bar').style.width = 100 - Player.getSongPercentRemaining() + '%';
			});

			Player.loadArrayBuffer(reader.result);

			document.getElementById('play-button').removeAttribute('disabled');

			$('#melody_player').fadeIn(700);
			//buildTracksHtml();
			play();
		}, false);
	}



	loadDataUri = function(dataUri) {
		Player = new MidiPlayer.Player(function(event) {
			if (event.name == 'Note on' && event.velocity > 0) {
				instrument.play(event.noteName, ac.currentTime, {gain:event.velocity/100});
				//document.querySelector('#track-' + event.track + ' code').innerHTML = JSON.stringify(event);
				//console.log(event);
			}

			document.getElementById('tempo-display').innerHTML = Player.tempo;
			document.getElementById('file-format-display').innerHTML = Player.format;
			document.getElementById('play-bar').style.width = 100 - Player.getSongPercentRemaining() + '%';
		});

		Player.loadDataUri(dataUri);

		document.getElementById('play-button').removeAttribute('disabled');

		//buildTracksHtml();

	}




});

