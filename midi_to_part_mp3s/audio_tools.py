import os
import re
import subprocess

import sox

# Using 0.0 caused audible clipping
GAIN_TO_AVOID_DISTORTION = -3.0


def convert_to_mp3(wavfile_path: str) -> str:
    mp3file_path = re.sub(r'\.wav$', '.mp3', wavfile_path)
    # Due to a quick with `lame`, the normal output goes to stderr, so we reduce
    # noisiness by redirecting to DEVNULL. Would be nice to show it in debug
    # mode.
    lame_process = subprocess.Popen([
        "lame", "--preset", "standard", wavfile_path, mp3file_path
    ],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    lame_process.wait()

    return mp3file_path


def compress_audio_dynamic_range(input_file_path):
    transformer = sox.Transformer()
    transformer.norm(GAIN_TO_AVOID_DISTORTION)
    # input and output files must differ for sox so we rename
    temp_name_for_operation = re.sub(r'\.wav$', '-bak.wav', input_file_path)
    os.rename(input_file_path, temp_name_for_operation)
    transformer.build(temp_name_for_operation, input_file_path)
    os.remove(temp_name_for_operation)


def combine_audio_files(input_files, output_file_path, input_volumes=None):
    combiner = sox.Combiner()
    combiner.norm(GAIN_TO_AVOID_DISTORTION)
    if input_volumes:
        # FIXME: Add back in input_volume variation once distortion confirmed
        # gone without that complication.
        combiner.build(input_files, output_file_path, 'mix')
    else:
        combiner.build(input_files, output_file_path, 'mix')


def convert_midi_to_wav(midifile_path: str, soundfont_path: str) -> str:
    wavfile_path = midifile_path.replace(".midi", ".wav")

    print("Converting {}".format(midifile_path))

    fluidsynth_process = subprocess.Popen(
        [
            "fluidsynth", "-F", wavfile_path, soundfont_path, midifile_path
        ], stdout=subprocess.DEVNULL
    )

    fluidsynth_process.wait()
    compress_audio_dynamic_range(wavfile_path)
    return wavfile_path
