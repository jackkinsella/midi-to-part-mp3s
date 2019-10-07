import os
import subprocess

from midi_to_part_mp3s.audio_tools import convert_midi_to_wav


class Part:
    def __init__(self, name: str, midi: str,
                 midifile_path: str, soundfont_path: str):
        self.name = name
        self.midi = midi
        self.midifile_path = midifile_path
        self.wavfile_path = convert_midi_to_wav(midifile_path, soundfont_path)
        self.midifile_path = midifile_path.replace(".midi", ".mp3")
