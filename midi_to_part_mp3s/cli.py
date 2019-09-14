# FIXME: For now, this file is ignored wrt mypy since I cannot figure out how to
# connect it to the argument parser module. A PR fixing types in this file would
# be joyously welcomed.

# type: ignore

import argparse

from midi_to_part_mp3s.custom_types import ConfigType, VoiceStringsType
from midi_to_part_mp3s.default_config import default_config
from midi_to_part_mp3s.splitter import Splitter
from typing import List


def help_string_for_voice(voice: VoiceStringsType):
    default = default_config["voices"][voice][0]
    return f'comma separated list of midi track IDs, defaults to "{default}"'


def get_parser() -> argparse.ArgumentParser:
    def convert_to_list(x): return list(map(int, x.split(',')))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--soprano",
        type=convert_to_list,
        help=help_string_for_voice("soprano")
    )
    parser.add_argument(
        "-a",
        "--alto",
        type=convert_to_list,
        help=help_string_for_voice("alto")
    )
    parser.add_argument(
        "-t",
        "--tenor",
        type=convert_to_list,
        help=help_string_for_voice("tenor")
    )
    parser.add_argument(
        "-b",
        "--bass",
        type=convert_to_list,
        help=help_string_for_voice("bass")
    )
    parser.add_argument(
        "-in",
        "--instrument",
        default=default_config["instrument"],
        type=int,
        help=('instrument for voices. Defaults to "49"')
    )
    parser.add_argument(
        "-iv",
        "--instrumental-volume",
        help="configure instrumental volume",
        type=float,
        default=default_config["instrumental_volume"]
    )
    parser.add_argument(
        "-i",
        "--instrumental-accompaniment",
        help='midi tracks that appear in all accompaniment mp3s e.g. piano or orchestra',
        nargs='+',
        type=int,
        default=default_config["instrumental_accompaniment"]
    )
    parser.add_argument(
        "-f",
        "--file-path",
        required=True,
        help='Input file to generate the tracks from. Can be Midi or \
                            MusicXML (.mid, .midi, .mxl, .musicxml)'
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        default=default_config["output_directory"],
        help=('Output directory')
    )
    parser.add_argument(
        "-sf",
        "--soundfont-path",
        default=default_config["soundfont_path"],
        help=('Soundfont path. Changing this gives you new sounds')
    )
    return parser


def user_has_set_all_voices(config):
    return all([config["soprano"], config["alto"], config["tenor"], config["bass"]])


def user_has_set_no_voices(config):
    return not any([config["soprano"], config["alto"], config["tenor"], config["bass"]])


def convert_cli_args_to_internal_config(argv: List) -> ConfigType:
    parsed_args = vars(get_parser().parse_args(argv))
    config = parsed_args.copy()

    if user_has_set_all_voices(parsed_args):
        config["voices"] = {
            "alto": config["alto"],
            "bass": config["bass"],
            "soprano": config["soprano"],
            "tenor": config["tenor"]
        }
    elif user_has_set_no_voices(parsed_args):
        config["voices"] = default_config["voices"]
    else:
        raise Exception("Please specify either no voices or all voices")

    # Delete top-level voices and get object conforming to expectations.
    del config["alto"]
    del config["bass"]
    del config["soprano"]
    del config["tenor"]

    return config


def main(argv: List) -> None:
    config: ConfigType = convert_cli_args_to_internal_config(argv)
    Splitter(config).split()
