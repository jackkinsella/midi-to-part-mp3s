import os
import sys
import shutil
from typing import List

import sox  # type: ignore
import mido  # type: ignore
import music21  # type: ignore

from midi_to_part_mp3s.dynamic_range_compression import compress_dynamic_range
from midi_to_part_mp3s.custom_types import ConfigType, VoiceStringsType
from midi_to_part_mp3s.part import Part
from midi_to_part_mp3s.file_format_converters import check_format

sung_parts: List[VoiceStringsType] = ['soprano', 'alto', 'bass', 'tenor']


class Splitter:
    def __init__(self, config: ConfigType):
        self.config = config

    def split(self):
        output_directory = self.config["output_directory"]
        prepare_output_directory(output_directory)
        converted_midi_file_path = check_format(self.config["file_path"], output_directory)
        self.__separate_tracks_into_mp3s(converted_midi_file_path)
        cleanup(output_directory)

    def __separate_tracks_into_mp3s(self, midifile_path: str) -> None:
        midi_data: mido.MidiFile = self.__ensure_midi_well_formatted(
            mido.MidiFile(midifile_path)
        )

        if self.config["compress_dynamic_range"]:
            midi_data = compress_dynamic_range(midi_data)

        solo_parts: List[Part] = []
        voices: list = self.__create_voices()
        self.__add_accompaniment(voices)
        for part_name, track_numbers, instrument in voices:
            solo_part: Part = self.__generate_solo_parts(midi_data, track_numbers,
                                                         part_name, instrument
                                                         )
            solo_parts.append(solo_part)

        part: Part
        for part in solo_parts:
            self.__generate_accompaniment(part, solo_parts)

        self.__generate_full_mp3(solo_parts)

    def __ensure_midi_well_formatted(self, midi_data: mido.MidiFile) -> mido.MidiFile:
        if self.__has_separate_tempo_map(midi_data.tracks[0]):
            return midi_data
        else:
            return self.__separate_out_tempo_map(midi_data)

    def __create_voices(self) -> list:
        """Creates a nested list of the voices with their assigned midi track number

        Returns:
            List[List] -- list of voices and their assigned midi track numbers
        """
        voices: List[List] = []
        tempo_map_track_number = 0
        sung_part: VoiceStringsType
        for sung_part in sung_parts:
            voice_midi_tracks = self.config["voices"][sung_part]
            if (voice_midi_tracks):
                for i in range(len(voice_midi_tracks)):
                    tracks = []
                    track_id = voice_midi_tracks[i]
                    tracks.append(tempo_map_track_number)
                    tracks.append(track_id)
                    instrument = self.config["instrument"]
                    voice = [sung_part + ' ' + str(i + 1), tracks, instrument]
                    voices.append(voice)
        return voices

    def __add_accompaniment(self, voices: list) -> None:
        """Edits the voices list to include the accompaniment voice

        Arguments:
            voices {list} -- list of voices and their assigned midi track numbers
        """
        if self.config["instrumental_accompaniment"]:
            voices.append(['accompaniment', self.config["instrumental_accompaniment"]])

    def __generate_solo_parts(self, midi_data: mido.MidiFile, track_numbers: List[int],
                              part_name: str, instrument_number: int) -> Part:
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
        midi.ticks_per_beat = midi_data.ticks_per_beat

        track_number: int
        for track_number in track_numbers:
            midi.tracks.append(midi_data.tracks[track_number])

        if part_name != 'accompaniment':
            self.__change_instrument(midi, instrument_number)
        new_file_path = "{}/{}.midi".format(self.config["output_directory"], part_name)
        midi.save(new_file_path)

        part = Part(name=part_name, midi=midi, midi_filepath=new_file_path,
                    soundfont_path=self.config["soundfont_path"]
                    )

        return part

    def __generate_accompaniment(self, own_part, solo_parts) -> None:
        combiner = sox.Combiner()

        accompaniment_volume_ratio = self.config["accompaniment_volume_ratio"]
        instrumental_volume_ratio = accompaniment_volume_ratio * self.config["instrumental_volume"]
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
            self.config["output_directory"], own_part.name)
        combiner.build(input_files, output_file_path, 'mix-power', input_volumes)

    def __generate_full_mp3(self, solo_parts: List[Part]) -> None:
        combiner = sox.Combiner()

        # docs https://pysox.readthedocs.io/en/latest/api.html
        input_files = [part.mp3_filepath() for part in solo_parts]
        output_file_path = "{}/all.mp3".format(self.config["output_directory"])
        combiner.build(input_files, output_file_path, 'mix-power')

    def __has_separate_tempo_map(self, track0: mido.midifiles.tracks.MidiTrack) -> bool:
        return not any(event.type == "note_on" for event in track0)

    def __separate_out_tempo_map(self, midi_data: mido.MidiFile) -> mido.MidiFile:
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

    def __change_instrument(self, midi_data: mido.MidiFile, program_number: int):
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
                program_change_message = mido.Message('program_change',
                                                      program=program_number)
                track.insert(0, program_change_message)


def cleanup(output_directory: str) -> None:
    def remove_temporary_midifiles() -> None:
        midi_file: str

        for midi_file in os.listdir(output_directory):
            if midi_file.endswith('.midi'):
                os.unlink(os.path.join(output_directory, midi_file))

    remove_temporary_midifiles()


def prepare_output_directory(output_directory: str) -> None:
    """ Ensures an empty output directory is available"""
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)

    os.makedirs(output_directory)
