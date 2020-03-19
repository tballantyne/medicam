function initVideo(token, room) {
	Twilio.Video.connect(token, {
		name: room,
		audio: true,
		video: true,
		preferredVideoCodecs: ['VP8', 'H264']
	}).then(room => {
		console.log(`Successfully joined a Room: ${room}`);

		room.localParticipant.tracks.forEach(publication => {
			if (publication.kind == "video") {
				const track = publication.track;
				document.getElementById('local-media').appendChild(track.attach());
			}
		});

		room.participants.forEach(participant => {
			console.log(`Participant "${participant.identity}" is connected to the Room`);
			handleParticipant(participant);
		});

		room.on('participantConnected', participant => {
			console.log(`A remote Participant connected: ${participant}`);
			document.getElementById('connection-status').innerText = "Connected";
			handleParticipant(participant);
		});

		room.on('participantDisconnected', participant => {
  			console.log(`Participant disconnected: ${participant.identity}`);
  			document.getElementById('connection-status').innerText = "Disconnected";
		});

	}, error => {
		console.error(`Unable to connect to Room: ${error.message}`);
	});
}

function handleParticipant(participant) {
	participant.tracks.forEach(publication => {
		if (publication.isSubscribed) {
			const track = publication.track;
			document.getElementById('remote-media').appendChild(track.attach());
		}
	});

	participant.on('trackSubscribed', track => {
		document.getElementById('remote-media').appendChild(track.attach());
	});
}
