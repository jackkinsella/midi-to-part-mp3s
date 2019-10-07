import os
import re
import subprocess

import sox

# Using 0.0 caused audible clipping
GAIN_TO_AVOID_DISTORTION = -3.0


def compress_audio_dynamic_range(input_file_path):
    transformer = sox.Transformer()
    transformer.norm(GAIN_TO_AVOID_DISTORTION)
    # input and output files must differ for sox so we rename
    temp_name_for_operation = re.sub(r'\.mp3$', '-bak.mp3', input_file_path)
    os.rename(input_file_path, temp_name_for_operation)
    transformer.build(temp_name_for_operation, input_file_path)
    os.remove(temp_name_for_operation)


def combine_audio_files(input_files, output_file_path, input_volumes=None):
    combiner = sox.Combiner()
    combiner.norm(GAIN_TO_AVOID_DISTORTION)
    if input_volumes:
        # TODO:
        combiner.build(input_files, output_file_path, 'mix')
    else:
        combiner.build(input_files, output_file_path, 'mix')
