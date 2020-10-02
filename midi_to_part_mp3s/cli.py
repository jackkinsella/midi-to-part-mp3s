# FIXME: For now, this file is ignored wrt mypy since I cannot figure out how to
# connect it to the argument parser module. A PR fixing types in this file would
# be joyously welcomed.

# type: ignore

import argparse

from midi_to_part_mp3s.custom_types import ConfigType, VoiceStringsType
from midi_to_part_mp3s.custom_types import SATB_VOICES
from midi_to_part_mp3s.default_config import default_config
from midi_to_part_mp3s.splitter import Splitter
from typing import List


def help_string_for_voice(voice: VoiceStringsType):
    if any(default_config["voices"][voice]):
        default = default_config["voices"][voice][0]
    else:
        default = "'disabled voice'"
    return f'comma separated list of midi track IDs, defaults to "{default}". -1 to skip track'


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def convert_to_list(x):
    return list(map(int, x.split(',')))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    voice: VoiceStringsType
    for voice in SATB_VOICES:
        # E.g. for soprano provides -s, -soprano -s2, soprano2
        parser.add_argument(
            f"-{voice[0]}",
            f"--{voice}",
            type=convert_to_list,
            help=help_string_for_voice(voice)
        )
        parser.add_argument(
            f"-{voice[0]}2",
            f"--{voice}2",
            type=convert_to_list,
            help=help_string_for_voice(f"{voice}2")
        )
    parser.add_argument(
        "-in",
        "--instrument",
        default=default_config["instrument"],
        type=int,
        help=('instrument for voices. Defaults to "49"')
    )
    parser.add_argument(
        "-tsf",
        "--tempo-scaling-factor",
        help="ratio of how much to scale tempo by",
        type=float,
        default=default_config["tempo_scaling_factor"]
    )
    parser.add_argument(
        "-av",
        "--accompaniment-volume-ratio",
        help="ratio of how loud accompanying voices should be in the "
        "accompaniment tracks",
        type=float,
        default=default_config["accompaniment_volume_ratio"]
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
        "-rif",
        "--retain-intermediate-files",
        type=str2bool,
        const=True,
        nargs='?',
        help='Keep the intermediate midi and wav files around instead of deleting them',
        default=default_config["retain_intermediate_files"]
    )
    parser.add_argument(
        "-gat",
        "--generate-accompaniment-tracks",
        type=str2bool,
        const=True,
        nargs='?',
        help='Generate tracks where the main voice is loud and the others are quiet',
        default=default_config["generate_accompaniment_tracks"]
    )
    parser.add_argument(
        "-gabot",
        "--generate-all-but-one-tracks",
        action='store_true',
        help='Generate tracks where the main voice is missing and the others are there',
        default=default_config["generate_all_but_one_tracks"]
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
    parser.add_argument(
        "-c",
        "--compress-dynamic-range",
        type=str2bool,
        default=default_config["compress_dynamic_range"],
        help="Gets rid of extreme differences in volume"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action='store_true',
        default=default_config["verbose"],
        help=('Print more debugging information')
    )
    parser.add_argument(
        "-la",
        "--log-all-midi-messages",
        action='store_true',
        default=default_config["log_all_midi_messages"],
        help=('Print every midi message (for extreme debugging)')
    )
    return parser


def user_has_set_all_voices(config):
    return all([config["soprano"], config["alto"],
                config["tenor"], config["bass"]])


def user_has_set_no_voices(config):
    return not any([config["soprano"], config["alto"],
                    config["tenor"], config["bass"]])


def convert_cli_args_to_internal_config(argv: List) -> ConfigType:
    parsed_args = vars(get_parser().parse_args(argv))
    config = parsed_args.copy()

    if user_has_set_all_voices(parsed_args):
        config["voices"] = {
            "alto": config["alto"],
            "alto2": config["alto2"],
            "bass": config["bass"],
            "bass2": config["bass2"],
            "soprano": config["soprano"],
            "soprano2": config["soprano2"],
            "tenor": config["tenor"],
            "tenor2": config["tenor2"]
        }
    elif user_has_set_no_voices(parsed_args):
        config["voices"] = default_config["voices"]
    else:
        raise Exception("Please specify either no voices or all voices")

    # Delete top-level voices and get object conforming to expectations.
    for voice in SATB_VOICES:
        del config[voice]

    if config["verbose"]:
        print("Parsed config:", config)

    return config


def main(argv: List) -> None:
    config: ConfigType = convert_cli_args_to_internal_config(argv)
    Splitter(config).split()
