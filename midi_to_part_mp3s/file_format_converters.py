import music21  # type: ignore
import re
import subprocess


def convert_to_mp3(wavfile_path: str) -> str:
    mp3file_path = re.sub(r'\.wav$', '.mp3', wavfile_path)
    print(f"Creating MP3 {mp3file_path}")
    # Due to a quick with `lame`, the normal output goes to stderr, so we reduce
    # noisiness by redirecting to DEVNULL. Would be nice to show it in debug
    # mode.
    lame_process = subprocess.Popen(
        ["lame", "--preset", "standard", wavfile_path, mp3file_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    lame_process.wait()

    return mp3file_path


def check_format(file_path: str, output_directory: str) -> str:
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
        return convert_music_xml_to_midi(file_path, output_directory)
    else:
        raise NameError(
            'The application currently only supports midi or MusicXML format')


def convert_music_xml_to_midi(file_path: str, output_directory: str) -> str:
    """Converts a MusicXML file to midi

    Arguments:
        file_path {str} -- file path of the the MusicXML file

    Returns:
        str -- path of the converted midi file after conversion
    """
    converted_file_path = output_directory + '/temp.midi'
    score: music21.stream.Score = music21.converter.parse(file_path)
    midi_file = music21.midi.translate.streamToMidiFile(score)
    midi_file.open(converted_file_path, 'wb')
    midi_file.write()
    midi_file.close()
    return converted_file_path
