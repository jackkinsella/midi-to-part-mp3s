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
    if file_path.endswith('.mid') or file_path.endswith('.midi'):
        return file_path
    elif file_path.endswith('.mxl') or file_path.endswith('.musicxml'):
        return convert_music_xml_to_midi(file_path, output_directory)
    else:
        raise NameError(
            'The application currently only supports midi or MusicXML format')


def convert_music_xml_to_midi(file_path: str, output_directory: str) -> str:
    # Must be 'mid' not "midi" to work with Musescore
    converted_file_path = output_directory + '/temp.mid'
    print("\nConverting to midi")
    # We expect the musescore executable to be available on PATH
    process = subprocess.Popen(
        ["mscore", "-o", converted_file_path, file_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    if process.wait() != 0:
        raise Exception("Problem executing mscore subprocess")

    return converted_file_path
