import mido


def analyze(mido: mido.MidiFile):
    print("Analyzing midi file\n")
    num_tracks = len(mido.tracks)
    print(f"Number of tracks: {num_tracks}\n")
    for index, track in enumerate(mido.tracks):
        track_name = track.name
        message_count = track.__len__()
        print(f" >Track {index}: {track_name}: {message_count} messages")
