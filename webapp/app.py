from flask import Flask, render_template, request, send_file, Response
from werkzeug import FileStorage
from zipfile import ZipFile
import uuid
import os
import shutil
from music21 import *
import json
from typing import List
from inspect import getsourcefile
# import from parent dir according to https://stackoverflow.com/a/9331002
import os.path as path, sys
current_dir = path.dirname(path.abspath(getsourcefile(lambda:0)))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])
import midi_to_part_mp3s
sys.path.pop(0)


app = Flask(__name__)

FILE: str = 'file'
SOPRANO: str = 'soprano'
ALTO: str = 'alto'
TENOR: str = 'tenor'
BASS: str = 'bass'
INSTRUMENT: str = 'instrument'
MUSICXML: str = 'musicxml'
OUTPUT: str = 'output'

TEMP_FOLDER: str = 'tmp'
OUTPUT_FOLDER: str = 'out'
FILENAME: str = 'part-mp3s.zip'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/midi-info", methods=['POST'])
def midi_info():
    random_folder_name = _check_tmp_folder()
    midi_file_name = _get_musicxml_file(random_folder_name)
    print(midi_file_name)
    score: stream.Score = converter.parse(midi_file_name)
    print(score)
    musicxml_filename = "%s/%s" % (random_folder_name, 'score.musicxml')
    score.write(fp=musicxml_filename)
    xml_content = None
    with open(musicxml_filename) as file_stream:
        xml_content = file_stream.read()
    response_dict = {}
    response_dict['musicxml'] = xml_content
    response_dict['parts'] = []
    part_stream = score.parts.stream()
    for part in part_stream:
        response_dict['parts'].append(part.id)
    return json.dumps(response_dict)


@app.route("/download", methods=['POST'])
def midi_to_mp3():
    random_folder_name = _check_tmp_folder()
    soprano_tracks = request.form.getlist(SOPRANO)
    alto_tracks = request.form.getlist(ALTO)
    tenor_tracks = request.form.getlist(TENOR)
    bass_tracks = request.form.getlist(BASS)
    instrument_id = request.form.get(INSTRUMENT)
    music_xml = request.form.get(MUSICXML)
    midi_file_path = _save_musicxml_file(random_folder_name, music_xml)

    print("soprano-tracks: %s, alto_tracks: %s, tenor_tracks: %s, bass_tracks: %s, instrument_id: %s, music_xml: %s characters" % (
        soprano_tracks, alto_tracks, tenor_tracks, bass_tracks, instrument_id, len(
            music_xml)
    ))

    output_folder, argument_list = _create_argument_list(midi_file_path, soprano_tracks, alto_tracks, tenor_tracks, bass_tracks, instrument_id, random_folder_name)
    print('Starting midi_to_part_mp3s with parameter list: %s' % argument_list)
    midi_to_part_mp3s.main(argument_list)

    return _send_zip_file(random_folder_name, output_folder)

def _create_argument_list(midi_file_path: str, soprano_tracks, alto_tracks, tenor_tracks, bass_tracks, instrument_id, random_folder_name) -> List[str]:
    argument_list: List[str] = ['-f', midi_file_path]
    _list_append_track_id(argument_list, SOPRANO, soprano_tracks)
    _list_append_track_id(argument_list, ALTO, alto_tracks)
    _list_append_track_id(argument_list, TENOR, tenor_tracks)
    _list_append_track_id(argument_list, BASS, bass_tracks)
    _single_append_argument(argument_list, INSTRUMENT, instrument_id)

    output_folder = '%s/%s' % (random_folder_name, OUTPUT_FOLDER)
    _single_append_argument(argument_list, OUTPUT, output_folder)
    return output_folder, argument_list

def _send_zip_file(folder_to_zip: str, output_folder: str):
    zip_file_name = '%s/%s' % (folder_to_zip, FILENAME)
    print ('Creating zip file: %s' % zip_file_name)
    with ZipFile(zip_file_name, 'w') as myzip:
        for file_name in os.listdir(output_folder):
            myzip.write(os.path.join(output_folder, file_name), file_name)
    
    #send_file is based on the web app directory, therefore need to access file absolute
    return send_file(os.path.abspath(zip_file_name), mimetype='application/zip',
                     attachment_filename='part-mp3s.zip',
                     as_attachment=True)


def _list_append_track_id(argument_list: List[str], parameter: str, track_id_list: List[str]) -> None:
    if(track_id_list):
        argument_list.append("--%s" % parameter)
        for track_id in track_id_list:
            # need to advance ID by 1 (midi track will have tempo map at track 0)
            midi_id = int(track_id) + 1
            argument_list.append(str(midi_id))


def _single_append_argument(argument_list: List[str], parameter: str, value: str) -> None:
    if(value):
        argument_list.append("--%s" % parameter)
        argument_list.append(value)


def _check_tmp_folder() -> None:
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    random_folder_name = uuid.uuid4()
    tmp_folder = "%s/%s" % (TEMP_FOLDER, random_folder_name)
    os.makedirs(tmp_folder)
    return tmp_folder


def _get_musicxml_file(temp_folder: str) -> str:
    music_xml_path = None
    try:
        midi_file: FileStorage = request.files[FILE]
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        music_xml_path = os.path.join(temp_folder, midi_file.filename)
        midi_file.save(music_xml_path)
    except Exception as e:
        print("File could not be fetched from the request: %s" % e)
    return music_xml_path


def _save_musicxml_file(temp_folder: str, music_xml: str) -> str:
    music_xml_path = None
    try:
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        music_xml_path = os.path.join(temp_folder, 'temp.musicxml')
        with open(music_xml_path, 'w') as file_stream:
            file_stream.write(music_xml)
    except Exception as e:
        print("musicXML could not be fetched from the request: %s" % e)
    return music_xml_path


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
