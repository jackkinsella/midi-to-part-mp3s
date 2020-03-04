import os
import shutil
import wget
from typing import List

import mido  # type: ignore

from midi_to_part_mp3s.midi_dynamic_range_compression import compress_midi_dynamic_range
from midi_to_part_mp3s.audio_tools import combine_audio_files
from midi_to_part_mp3s.custom_types import ConfigType, VoiceStringsType
from midi_to_part_mp3s.part import Part
from midi_to_part_mp3s.file_format_converters import check_format, convert_to_mp3
from midi_to_part_mp3s.analysis import analyze, is_split_by_channel, number_of_channels

sung_parts: List[VoiceStringsType] = ['soprano',
                                      'soprano2', 'alto', 'bass', 'tenor']


class Splitter:
    def __init__(self, config: ConfigType):
        self.config = config

    def split(self):
        output_directory = self.config["output_directory"]
        prepare_output_directory(output_directory)
        converted_midifile_path = check_format(
            self.__local_file(), output_directory
        )
        self.__separate_tracks_into_wavs(converted_midifile_path)
        create_mp3s_from_wavs(output_directory)
        cleanup(output_directory)

    def __separate_tracks_into_wavs(self, midifile_path: str) -> None:
        midi_data: mido.MidiFile = mido.MidiFile(midifile_path)
        # FIXME: This does not belong here
        analyze(midi_data, self.config["log_all_midi_messages"])
        # FIXME: typehinting not working here
        midi_data = self.__ensure_separate_tempo_track(
            mido.MidiFile(midifile_path)
        )
        if self.config["compress_dynamic_range"]:
            midi_data = compress_midi_dynamic_range(midi_data)

        solo_parts: List[Part] = []
        voices: list = self.__create_voices()
        self.__add_accompaniment(voices)
        for part_name, track_numbers, instrument in voices:
            print("Spliting out {} midi file".format(part_name))
            solo_part: Part = self.__generate_solo_parts(
                midi_data, track_numbers, part_name, instrument
            )
            solo_parts.append(solo_part)

        part: Part
        if self.config["generate_all_but_one_tracks"]:
            for part in solo_parts:
                self.__generate_all_but_one_part_track(part, solo_parts)

        if self.config["generate_accompaniment_tracks"]:
            for part in solo_parts:
                self.__generate_accompaniment(part, solo_parts)

        self.__generate_full_wav(solo_parts)

    def __ensure_separate_tempo_track(
        self, midi_data: mido.MidiFile
    ) -> mido.MidiFile:
        number_of_tracks = len(midi_data.tracks)
        self.__log(f"Input file has {number_of_tracks} tracks")

        if self.__has_separate_tempo_map(midi_data.tracks[0]):
            self.__log("Separate tempo map detected")
            return midi_data
        else:
            self.__log("Generating a separate tempo map track")
            return self.__separate_out_tempo_map(midi_data)

    # FIXME: The naming is confusing. Also the output as list hides the fact
    # that this produces something structured: {name: "Soprano 1", midi_tracks:
    # [0, 3], instrument: 0}
    def __create_voices(self) -> list:
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
                    name = sung_part if i == 0 else sung_part + \
                        ' ' + str(i + 1)
                    voice = [name, tracks, instrument]
                    voices.append(voice)
        self.__log(f"Voices generated {voices}")
        return voices

    def __add_accompaniment(self, voices: list) -> None:
        if self.config["instrumental_accompaniment"]:
            voices.append(
                ['accompaniment', self.config["instrumental_accompaniment"]])

    # FIXME: This belongs elsewhere, as does its callr.
    def __set_bpm(self, midi: mido.MidiFile, bpm: int) -> mido.MidiFile:
        for track in midi.tracks:
            for message in track:
                if message.is_meta and message.type == "set_tempo":
                    message.tempo = mido.bpm2tempo(bpm)

        return midi

    def __generate_solo_parts(
            self, midi_data: mido.MidiFile, track_numbers: List[int],
            part_name: str, instrument_number: int) -> Part:
        midi: mido.MidiFile = mido.MidiFile()
        midi.ticks_per_beat = midi_data.ticks_per_beat

        track_number: int
        for track_number in track_numbers:
            if is_split_by_channel(midi_data):
                for channel_number in range(number_of_channels(midi_data)):
                    midi.tracks.append(self.__extract_channel(channel_number,
                                                              midi_data.tracks[-1]))
            else:
                midi.tracks.append(midi_data.tracks[track_number])

        if part_name != 'accompaniment':
            self.__change_instrument(midi, instrument_number)
        new_file_path = "{}/{}.midi".format(
            self.config["output_directory"], part_name)
        midi.save(new_file_path)

        part = Part(name=part_name, midi=midi, midifile_path=new_file_path,
                    soundfont_path=self.config["soundfont_path"]
                    )

        return part

    def __extract_channel(
            self, channel_number: int, track: List[mido.Message]
    ) -> List[mido.Message]:
        messages = []
        for message in track:
            if message.type == "note_on" and message.channel == channel_number:
                next
            messages.append(message)

        return messages

    def __generate_all_but_one_part_track(
            self, excluded_part, solo_parts
    ) -> None:
        input_files = [
            part.wavfile_path for part in solo_parts
            if part.name != excluded_part.name
        ]

        output_file_path = "{}/all except {}.wav".format(
            self.config["output_directory"], excluded_part.name
        )
        combine_audio_files(input_files, output_file_path)

    def __generate_accompaniment(self, own_part, solo_parts) -> None:
        accompaniment_volume_ratio = self.config["accompaniment_volume_ratio"]
        instrumental_volume_ratio = (accompaniment_volume_ratio *
                                     self.config["instrumental_volume"])
        input_volumes = []
        input_files = []
        for part in solo_parts:
            is_own_part = part.name == own_part.name
            is_instrumental = part.name == 'accompaniment'

            input_files.append(part.wavfile_path)

            if is_own_part:
                input_volumes.append(1.0)
            elif is_instrumental:
                input_volumes.append(instrumental_volume_ratio)
            else:
                input_volumes.append(accompaniment_volume_ratio)

        output_file_path = "{}/{} with accompaniment.wav".format(
            self.config["output_directory"], own_part.name)
        combine_audio_files(input_files, output_file_path, input_volumes)

    def __generate_full_wav(self, solo_parts: List[Part]) -> None:
        input_files = [part.wavfile_path for part in solo_parts]
        output_file_path = "{}/all.wav".format(self.config["output_directory"])
        combine_audio_files(input_files, output_file_path)

    def __has_separate_tempo_map(
            self, track0: mido.midifiles.tracks.MidiTrack
    ) -> bool:
        return not any(message.type == "note_on" for message in track0)

    def __separate_out_tempo_map(
            self, midi_data: mido.MidiFile
    ) -> mido.MidiFile:
        tempo_map_track = []
        initial_track = midi_data.tracks[0]
        rewritten_initial_track = []

        for event in initial_track:
            if event.is_meta:
                if event.type in ["instrument_name", "key_signature"]:
                    rewritten_initial_track.append(event)
                else:
                    rewritten_initial_track.append(event)
                    tempo_map_track.append(event)
            else:
                rewritten_initial_track.append(event)

        rewritten_midi = mido.MidiFile()
        rewritten_midi.ticks_per_beat = midi_data.ticks_per_beat
        rewritten_midi.tracks.append(tempo_map_track)
        rewritten_midi.tracks.append(rewritten_initial_track)
        for track in midi_data.tracks[1:]:
            rewritten_midi.tracks.append(track)

        return rewritten_midi

    def __change_instrument(
            self, midi_data: mido.MidiFile, program_number: int
    ):
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

    def __local_file(self):
        """Downloads file if at a remote URL

        """
        if self.config["file_path"].startswith("http"):
            self.__log("File not found locally....downloading ")
            return wget.download(self.config["file_path"], out="./tmp")
        else:
            return self.config["file_path"]

    def __log(self, message):
        if self.config["verbose"]:
            print(message)


def cleanup(output_directory: str) -> None:
    for file in os.listdir(output_directory):
        if not file.endswith('.mp3'):
            os.unlink(os.path.join(output_directory, file))


def prepare_output_directory(output_directory: str) -> None:
    """ Ensures an empty output directory is available"""
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)

    os.makedirs(output_directory)


def create_mp3s_from_wavs(directory: str):
    for file in os.listdir(directory):
        if file.endswith('.wav'):
            convert_to_mp3(os.path.join(directory, file))
