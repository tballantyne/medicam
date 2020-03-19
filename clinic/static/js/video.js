function initVideo(token, room) {
	Twilio.Video.createLocalVideoTrack().then(track => {
		const localMediaContainer = document.getElementById('local-media');
		localMediaContainer.appendChild(track.attach());
	});

	Twilio.Video.connect(token, {
		name: room,
		audio: true,
		video: { width: 640 }
	}).then(room => {
		console.log(`Successfully joined a Room: ${room}`);
		room.on('participantConnected', participant => {
			console.log(`A remote Participant connected: ${participant}`);
			document.getElementById('connection-status').innerText = "Connected";
			participant.tracks.forEach(publication => {
				if (publication.isSubscribed) {
					const track = publication.track;
					document.getElementById('remote-media').appendChild(track.attach());
				}
			});
			participant.on('trackSubscribed', track => {
				document.getElementById('remote-media').appendChild(track.attach());
			});
		});
		room.on('participantDisconnected', participant => {
  			console.log(`Participant disconnected: ${participant.identity}`);
  			document.getElementById('connection-status').innerText = "Disconnected";
		});
	}, error => {
		console.error(`Unable to connect to Room: ${error.message}`);
	});
}
