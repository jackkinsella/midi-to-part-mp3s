import mido


def analyze(mido: mido.MidiFile, log_all_midi_messages=False):
    print("Analyzing midi file\n")
    num_tracks = len(mido.tracks)
    print(f"Number of tracks: {num_tracks}\n")
    for index, track in enumerate(mido.tracks):
        if hasattr(track, "name"):
            track_name = track.name
        else:
            track_name = f"Track {index}"
        number_of_midi_channels = len(
            set(message.channel for message in track if not message.is_meta)
        )
        message_count = track.__len__()
        print(f"> Track {index}: {track_name}: {number_of_midi_channels}"
              f" channels {message_count} messages")
        if log_all_midi_messages:
            print("\n\n")
            for message in track:
                print(message)
