import midi_to_part_mp3s
import unittest
import shutil
import os
from typing import List

# allow to import modules from parent dir (https://stackoverflow.com/a/33532002/2641951)
from inspect import getsourcefile
import os.path as path
import sys
current_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])


class TestMoreVoices(unittest.TestCase):
    def _cleanup_output_dir(self):
        if os.path.exists(midi_to_part_mp3s.output_directory):
            shutil.rmtree(midi_to_part_mp3s.output_directory)

    def setUp(self):
        self._cleanup_output_dir()
        return super().setUp()

    def tearDown(self):
        self._cleanup_output_dir()
        return super().tearDown()

    def test_defaut_settings(self):
        arguments: List[str] = [
            "-f", "./tests/fixtures/Brahms-Da-unten-im-Tale.mid"
        ]
        expected_filenames = [
            'tenor 1 with accompaniment.mp3', 'soprano 1.mp3', 'tenor 1.mp3',
            'bass 1.mp3', 'soprano 1 with accompaniment.mp3',
            'alto 1 with accompaniment.mp3', 'alto 1.mp3', 'all.mp3',
            'bass 1 with accompaniment.mp3'
        ]
        self._simple_file_list_check(arguments, expected_filenames)

    def test_ssaa(self):
        arguments: List[str] = [
            "-f", "./tests/fixtures/Brahms-Da-unten-im-Tale.mid", '--soprano',
            '1,2', '--alto', '3,4'
        ]
        expected_filenames = [
            'soprano 1.mp3', 'soprano 1 with accompaniment.mp3',
            'soprano 2.mp3', 'soprano 2 with accompaniment.mp3', 'alto 1.mp3',
            'alto 1 with accompaniment.mp3', 'alto 2.mp3',
            'alto 2 with accompaniment.mp3', 'all.mp3'
        ]
        self._simple_file_list_check(arguments, expected_filenames)

    def test_ssaattbb(self):
        arguments: List[str] = [
            "-f", "./tests/fixtures/Abendlied-Rheinberger.mxl", '--soprano',
            '1,2', '--alto', '3,4', '--tenor', '5,6', '--bass', '7,8'
        ]
        expected_filenames = [
            'soprano 1.mp3', 'soprano 1 with accompaniment.mp3',
            'soprano 2.mp3', 'soprano 2 with accompaniment.mp3', 'alto 1.mp3',
            'alto 1 with accompaniment.mp3', 'alto 2.mp3',
            'alto 2 with accompaniment.mp3', 'tenor 1.mp3',
            'tenor 1 with accompaniment.mp3', 'tenor 2.mp3',
            'tenor 2 with accompaniment.mp3', 'bass 1.mp3',
            'bass 1 with accompaniment.mp3', 'bass 2.mp3',
            'bass 2 with accompaniment.mp3', 'all.mp3'
        ]
        self._simple_file_list_check(arguments, expected_filenames)

    def _simple_file_list_check(self, arguments: List[str],
                                expected_filenames: List[str]):
        midi_to_part_mp3s.main(arguments)
        filenames: List[str] = os.listdir(midi_to_part_mp3s.output_directory)
        self.assertCountEqual(filenames, expected_filenames)


if __name__ == '__main__':
    unittest.main()
