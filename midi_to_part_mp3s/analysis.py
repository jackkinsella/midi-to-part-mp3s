import mido

def number_of_voices_in_channel(track: mido.MidiTrack):
    note_on_messages_with_velocity = filter(
        lambda message: message.type == "note_on" and message.velocity > 0
        ,track
        )
    # ignore first element since starts at time 0 naturally often
    longest_run_simultaneous = 1
    current_run = 1
    for message in (list(note_on_messages_with_velocity))[1:]:
        # print(message)
        if message.time == 0:
            current_run+=1
            if current_run > longest_run_simultaneous:
                longest_run_simultaneous = current_run
        else:
            current_run = 0

    return longest_run_simultaneous



def analyze(midi: mido.MidiFile, log_all_midi_messages=False) -> None:
    print("Analyzing midi file\n")
    print(f"BPM: {bpm(midi)}\n")
    print(f"Number of tracks: {number_of_tracks(midi)}\n")
    for index, track in enumerate(midi.tracks):
        print(f"Track {index}: {number_of_voices_in_channel(track)} voices")
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
