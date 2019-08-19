import argparse

from midi_to_part_mp3s.custom_types import ConfigType, VoiceStringsType
from midi_to_part_mp3s.default_config import default_config
from midi_to_part_mp3s.splitter import Splitter
from typing import List


def help_string_for_voice(voice: VoiceStringsType):
    default = default_config[voice][0]
    return f'comma separated list of midi track IDs, defaults to "{default}"'


def get_parser() -> argparse.ArgumentParser:
    def convert_to_list(x): return list(map(int, x.split(',')))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--soprano",
        type=convert_to_list,
        default=default_config["soprano"],
        help=help_string_for_voice("soprano")
    )
    parser.add_argument(
        "-a",
        "--alto",
        type=convert_to_list,
        default=default_config["alto"],
        help=help_string_for_voice("alto")
    )
    parser.add_argument(
        "-t",
        "--tenor",
        type=convert_to_list,
        default=default_config["tenor"],
        help=help_string_for_voice("tenor")
    )
    parser.add_argument(
        "-b",
        "--bass",
        type=convert_to_list,
        default=default_config["bass"],
        help=help_string_for_voice("bass")
    )
    parser.add_argument(
        "-in",
        "--instrument",
        default=default_config["instrument"],
        type=int,
        help=('instrument for voices. Defaults to "49"'))
    parser.add_argument("-iv",
                        "--instrumental-volume",
                        help="configure instrumental volume",
                        type=float,
                        default=default_config["instrumental_volume"])
    parser.add_argument("-i",
                        "--instrumental-accompaniment",
                        help='midi tracks that \
          appear in all accompaniment mp3s e.g. piano or orchestra',
                        nargs='+',
                        type=int,
                        default=default_config["instrumental_accompaniment"])
    required_named = parser.add_argument_group('mandatory argument')
    required_named.add_argument(
        "-f",
        "--file-path",
        required=True,
        help='Input file to generate the tracks from. Can be Midi or \
                            MusicXML (.mid, .midi, .mxl, .musicxml)')
    return parser


# TODO: Add types for argv
# TODO2: Maybe combine with main method once working again
def parse_and_set_defaults(argv: List) -> ConfigType:
    parsed_args = get_parser().parse_args(argv)
    config: ConfigType = {**default_config, **vars(parsed_args)}
    return config


def main(argv: List) -> None:
    config = parse_and_set_defaults(argv)
    Splitter(config).split()
