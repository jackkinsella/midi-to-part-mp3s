import os
import re
import subprocess

import sox


def compress_audio_dynamic_range(input_file_path, gain_db):
    transformer = sox.Transformer()
    transformer.norm(gain_db)
    # input and output files must differ for sox so we rename
    temp_name_for_operation = re.sub(r'\.wav$', '-bak.wav', input_file_path)
    os.rename(input_file_path, temp_name_for_operation)
    transformer.build(temp_name_for_operation, input_file_path)
    os.remove(temp_name_for_operation)


def combine_audio_files(input_files, output_file_path, input_volumes=None):
    combiner = sox.Combiner()
    combiner.set_input_format(["wav"] * len(input_files))
    gain_to_avoid_clipping = -3.0
    combiner.gain(gain_to_avoid_clipping)

    combiner.build(input_files, output_file_path, 'mix', input_volumes)


def convert_midi_to_wav(midifile_path: str, soundfont_path: str) -> str:
    wavfile_path = midifile_path.replace(".midi", ".wav")

    print("Generating temporary wav {}".format(wavfile_path))

    # The files are saved with 24bits to give more space for editing (e.g.
    # possible information loss due to volume reduction pre-mixing)
    fluidsynth_process = subprocess.Popen([
        "fluidsynth", "-O", "s16", "-F", wavfile_path, soundfont_path,
        midifile_path
    ],
        stdout=subprocess.DEVNULL)

    fluidsynth_process.wait()
    gain_to_leave_room_for_mixing = -12
    compress_audio_dynamic_range(wavfile_path, gain_to_leave_room_for_mixing)
    return wavfile_path
