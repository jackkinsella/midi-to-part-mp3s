#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
from typing import List, Dict

import sox  # type: ignore
import mido  # type: ignore
import music21  # type: ignore

output_directory = './output'
soundfont_path = "./soundfonts/timbres-of-heaven.sf2"
sung_parts = ['soprano', 'alto', 'bass', 'tenor']
# instrument choices based off advice given here: http://www3.cpdl.org/wiki/index.php/User:Robert_Urmann
MAPPING = {
    "soprano": 76,  # pan flute
    "alto": 75,  # recorder
    "tenor": 49,  # string ensemble 1
    "bass": 50  # string ensemble 2
}
args = None


class Part:
    def __init__(self, name: str = '', midi: str = '', midi_filepath: str = ''):
        self.name = name
        self.midi = midi
        self.midi_filepath = midi_filepath
        convert_midi_to_mp3(midi_filepath)

    def mp3_filepath(self) -> str:
        return self.midi_filepath.replace(".midi", ".mp3")


def check_format(file_path: str) -> str:
    """If the format is midi, proceed. If the format is MusicXML, convert to midi.

    Arguments:
        file_path {[str]} -- path of the file to convert

    Raises:
        NameError: Raised if trying to convert a format not supported by the script

    Returns:
        str -- midi file name (original or converted midi file)
    """
    if file_path.endswith('.mid') or file_path.endswith('.midi'):
        return file_path
    elif file_path.endswith('.mxl') or file_path.endswith('.musicxml'):
        return convert_music_xml_to_midi(file_path)
    else:
        raise NameError(
            'The application currently only supports midi or MusicXML format')


def convert_music_xml_to_midi(file_path: str) -> str:
    """Converts a MusicXML file to midi

    Arguments:
        file_path {str} -- file path of the the MusicXML file

    Returns:
        str -- path of the converted midi file after conversion
    """
    converted_file_path = args.output + '/temp.midi'
    score: music21.stream.Score = music21.converter.parse(file_path)
    midi_file = music21.midi.translate.streamToMidiFile(score)
    midi_file.open(converted_file_path, 'wb')
    midi_file.write()
    midi_file.close()
    return converted_file_path


def track_names(midi_data) -> List[str]:
    return list(map(lambda track: track.name, midi_data.tracks))


def instrument_number_for_part(part: str) -> int:
    """Fetches the instrument index from the mapping. In case of an instrument
    parameter this instrument is returned instead of the default mapping

    Arguments:
        part {str} -- name of the part

    Returns:
        int -- integer index of an instrument
    """
    global args
    if (args.instrument != None):
        return args.instrument
    else:
        return MAPPING[part]


def generate_solo_parts(midi_data: mido.MidiFile, track_numbers: List[int], part_name: str, instrument_number: int) -> Part:
    """Generates a solo part and returns a Part object describing it

    Arguments:
        midi_data {mido.MidiFile} -- original midi data
        track_numbers {List[int]} -- numbers of the tracks to include in the solo parts
        part_name {str} -- name of the past
        instrument_number {int} -- id of the instrument in the configured soundfont

    Returns:
        Part -- generated Part object
    """
    midi: mido.MidiFile = mido.MidiFile()
    midi.ticks_per_beat: int = midi_data.ticks_per_beat

    track_number: int
    for track_number in track_numbers:
        midi.tracks.append(midi_data.tracks[track_number])

    if part_name != 'accompaniment':
        change_instrument(midi, instrument_number)
    new_file_path = "{}/{}.midi".format(args.output, part_name)
    midi.save(new_file_path)

    part = Part(name=part_name, midi=midi, midi_filepath=new_file_path)

    return part


def convert_midi_to_mp3(midifile_path: str) -> None:
    """Converts the midi file to mp3 format

    Arguments:
        midifile_path {str} -- path to the midi file

    Returns:
        None -- does not return anything. The file is created on the file system using fluidsynth
    """
    output_base_filename = os.path.splitext(midifile_path)[0]
    # TODO: Hide output unless debug option on... probably need subprocess.run
    os.system("fluidsynth -r 44100 -R 1 -E little -T raw -F - -O s16 '{}' '{}' | lame --signed -s 44100 -r - '{}.mp3'".format(
        soundfont_path, midifile_path, output_base_filename
    ))


def change_instrument(midi_data: mido.MidiFile, program_number: int):
    """Changes the instrument in all tracks of the given midi_data
    object to the instrument identified by program_number

    Arguments:
        midi_data {mido.MidiFile} -- midi data object
        program_number {int} -- instrument identifier
    """
    track: mido.MidiTrack
    for track in midi_data.tracks:
        found = None
        message: mido.Message
        for message in track:
            if message.type == 'program_change':
                found = True
                message.program = program_number
        if not found:
            program_change_message = mido.Message(
                'program_change', program=program_number)
            track.insert(0, program_change_message)


def generate_accompaniment(own_part, solo_parts) -> None:
    combiner = sox.Combiner()

    accompaniment_volume_ratio = 0.33
    instrumental_volume_ratio = accompaniment_volume_ratio * args.instrumental_volume
    input_volumes = []
    input_files = []
    for part in solo_parts:
        is_own_part = part.name == own_part.name
        is_instrumental = part.name == 'accompaniment'

        input_files.append(part.mp3_filepath())

        if is_own_part:
            input_volumes.append(1.0)
        elif is_instrumental:
            input_volumes.append(instrumental_volume_ratio)
        else:
            input_volumes.append(accompaniment_volume_ratio)

    output_file_path = "{}/{} with accompaniment.mp3".format(
        args.output, own_part.name)
    combiner.build(input_files, output_file_path, 'mix-power', input_volumes)


def generate_full_mp3(solo_parts: List[Part]) -> None:
    combiner = sox.Combiner()

    # docs https://pysox.readthedocs.io/en/latest/api.html
    input_files = [part.mp3_filepath() for part in solo_parts]
    output_file_path = "{}/all.mp3".format(args.output)
    combiner.build(input_files, output_file_path, 'mix-power')


def has_separate_tempo_map(track0: mido.midifiles.tracks.MidiTrack) -> bool:
    return not any(event.type == "note_on" for event in track0)


def separate_out_tempo_map(midi_data: mido.MidiFile) -> mido.MidiFile:
    tempo_map = []
    track1 = []

    for event in midi_data.tracks[0]:
        if event.is_meta:
            if event.type in ["instrument_name", "key_signature"]:
                track1.append(event)
            else:
                track1.append(event)
                tempo_map.append(event)
        else:
            track1.append(event)

    midi = mido.MidiFile()
    midi.ticks_per_beat = midi_data.ticks_per_beat

    midi.tracks.append(tempo_map)
    midi.tracks.append(track1)
    for track in midi_data.tracks[1:]:
        midi.tracks.append(track)

    return midi


def ensure_midi_well_formatted(midi_data: mido.MidiFile) -> mido.MidiFile:
    if has_separate_tempo_map(midi_data.tracks[0]):
        return midi_data
    else:
        return separate_out_tempo_map(midi_data)


def separate_tracks_into_mp3s(args: argparse.Namespace, midifile_path: str) -> None:
    midi_data: mido.MidiFile = ensure_midi_well_formatted(
        mido.MidiFile(midifile_path))
    solo_parts: List[Part] = []
    voices: list = create_voices()
    add_accompaniment(voices)
    for part_name, track_numbers, instrument in voices:
        solo_part: Part = generate_solo_parts(
            midi_data, track_numbers, part_name, instrument)
        solo_parts.append(solo_part)

    part: Part
    for part in solo_parts:
        generate_accompaniment(part, solo_parts)

    generate_full_mp3(solo_parts)


def create_voices() -> list:
    """Creates a nested list of the voices with their assigned midi track number

    Returns:
        List[List] -- list of voices and their assigned midi track numbers
    """
    voices: List[List] = []
    tempo_map_track_number = 0
    sung_part: str
    for sung_part in sung_parts:
        voice_midi_tracks = vars(args)[sung_part]
        if(voice_midi_tracks):
            for i in range(len(voice_midi_tracks)):
                tracks = []
                track_id = voice_midi_tracks[i]
                tracks.append(tempo_map_track_number)
                tracks.append(track_id)
                instrument = instrument_number_for_part(sung_part)
                voice = [sung_part + ' ' + str(i+1), tracks, instrument]
                voices.append(voice)
    return voices


def add_accompaniment(voices: list) -> None:
    """Edits the voices list to include the accompaniment voice

    Arguments:
        voices {list} -- list of voices and their assigned midi track numbers
    """
    if args.instrumental_accompaniment:
        voices.append(
            ['accompaniment', args.instrumental_accompaniment, None])


def cleanup() -> None:
    remove_temporary_midifiles()


def prepare_output_directory() -> None:
    """ Ensures an empty output directory is available"""
    if os.path.exists(args.output):
        shutil.rmtree(args.output)

    os.makedirs(args.output)




def remove_temporary_midifiles() -> None:
    midi_file: str
    for midi_file in os.listdir(args.output):
        if midi_file.endswith('.midi'):
            os.unlink(os.path.join(args.output, midi_file))


def set_defaults(args: argparse.Namespace) -> None:
    """Sets the soprano, alto, tenor and bass voices
    to the default tracks 1, 2, 3 and 4, if no track has been defined.
    This allows a SSAA or TTBB API setting without the need to overwrite
    defaults, i.e.:
    midi-to-part-mp3s your-midi.mid --soprano 1 2 --alto 3 4
    midi-to-part-mp3s your-midi.mid --tenor 1 2 --bass 3 4

    Arguments:
        args {argparse.Namespace} -- Original arguments

    Returns:
        None -- The args will be overwritten in the original args object
    """
    if (args.soprano == None and args.alto == None and
            args.tenor == None and args.bass == None):
        args.soprano = [1]
        args.alto = [2]
        args.tenor = [3]
        args.bass = [4]
    else:
        if args.soprano:
            args.soprano = [int(track) for track in args.soprano.split(',')]
        if args.alto:
            args.alto = [int(track) for track in args.alto.split(',')]
        if args.tenor:
            args.tenor = [int(track) for track in args.tenor.split(',')]
        if args.bass:
            args.bass = [int(track) for track in args.bass.split(',')]


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--soprano", type=str,
                        help='comma separated list of midi track IDs, defaults to "1"')
    parser.add_argument("-a", "--alto", type=str,
                        help='comma separated list of midi track IDs, defaults to "2"')
    parser.add_argument("-t", "--tenor", type=str,
                        help='comma separated list of midi track IDs, defaults to "3"')
    parser.add_argument("-b", "--bass", type=str,
                        help='comma separated list of midi track IDs, defaults to "4"')
    parser.add_argument("-in", "--instrument", type=int,
                        help=('instrument that should be used for all voices instead \
                              of the advice given at cpdl.org'))
    parser.add_argument("-iv", "--instrumental-volume",
                        help="configure instrumental volume", type=float, default=2.0)
    parser.add_argument("-i", "--instrumental-accompaniment", help='midi tracks that \
          appear in all accompaniment mp3s e.g. piano or orchestra', nargs='+',
                        type=int, default=[])
    parser.add_argument("-o", "--output", type=str, default=output_directory,
                        help="Output folder for the files. Defaults to './output'")
    requiredNamed = parser.add_argument_group('mandatory argument')
    requiredNamed.add_argument("-f", "--file-path", required=True,
                               help='Input file to generate the tracks from. Can be Midi or \
                            MusicXML (.mid, .midi, .mxl, .musicxml)')
    return parser


def main(sys_args):
    parser = get_parser()
    global args
    args = parser.parse_args(sys_args)
    set_defaults(args)
    prepare_output_directory()
    midi_file_path = check_format(args.file_path)
    separate_tracks_into_mp3s(args, midi_file_path)
    cleanup()


if __name__ == "__main__":
    main(sys.argv[1:])
