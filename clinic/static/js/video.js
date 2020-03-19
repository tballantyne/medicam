function initVideo(token, room) {
	Twilio.Video.connect(token, {
		name: room,
		audio: true,
		video: { width: 640 }
	}).then(room => {
		console.log(`Successfully joined a Room: ${room}`);
		room.on('participantConnected', participant => {
			console.log(`A remote Participant connected: ${participant}`);
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
	}, error => {
		console.error(`Unable to connect to Room: ${error.message}`);
	});
}
