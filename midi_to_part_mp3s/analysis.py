import mido


def analyze(midi: mido.MidiFile, log_all_midi_messages=False) -> None:
    print("Analyzing midi file\n")
    print(f"BPM: {bpm(midi)}\n")
    print(f"Number of tracks: {number_of_tracks(midi)}\n")
    if is_split_by_channel(midi):
        print("Split by channel\n")
    else:
        print("Split by track\n")
    for index, track in enumerate(midi.tracks):
        if hasattr(track, "name"):
            track_name = track.name
        else:
            track_name = f"Track {index}"
        message_count = track.__len__()
        print(f"> Track {index}: {track_name}:"
              f" {number_of_channels(track)}"
              f" channels {message_count} messages")
        if log_all_midi_messages:
            print("\n\n")
            for message in track:
                print(message)


def number_of_channels(track: mido.MidiTrack) -> int:
    return len(
        set(message.channel for message in track if not message.is_meta)
    )


def number_of_tracks(midi: mido.MidiFile) -> int:
    return len(midi.tracks)


def bpm(midi: mido.MidiFile) -> int:
    for track in midi.tracks:
        for message in track:
            if message.is_meta and message.type == "set_tempo":
                return int(mido.tempo2bpm(message.tempo))
    raise Exception("Not set_tempo message found")


def is_split_by_channel(midi: mido.MidiFile) -> bool:
    last_track = midi.tracks[-1]
    if number_of_tracks(midi) <= 2 and number_of_channels(last_track) > 1:
        return True
    else:
        return False
