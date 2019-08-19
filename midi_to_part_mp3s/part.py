import os


class Part:
    def __init__(self, name: str, midi: str,
                 midi_filepath: str, soundfont_path: str):
        self.name = name
        self.midi = midi
        self.midi_filepath = midi_filepath
        self.convert_midi_to_mp3(midi_filepath, soundfont_path)

    # This likely belongs elsewhere, like an audio module
    def convert_midi_to_mp3(self, midifile_path: str, soundfont_path: str) -> None:
        """Converts the midi file to mp3 format

        Arguments:
            midifile_path {str} -- path to the midi file

        Returns:
            None -- does not return anything. The file is created on the file system using fluidsynth
        """
        output_base_filename = os.path.splitext(midifile_path)[0]
        # TODO: Hide output unless debug option on... probably need subprocess.run
        os.system(
            "fluidsynth -r 44100 -R 1 -E little -T raw -F - -O s16 '{}' '{}' | lame --signed -s 44100 -r - '{}.mp3'"
            .format(soundfont_path, midifile_path, output_base_filename))

    def mp3_filepath(self) -> str:
        return self.midi_filepath.replace(".midi", ".mp3")
