import midi_to_part_mp3s
import unittest
import argparse
from typing import List

# allow to import modules from parent dir
# (https://stackoverflow.com/a/33532002/2641951)
from inspect import getsourcefile
import os.path as path
import sys
current_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, current_dir[:current_dir.rfind(path.sep)])


class TestArgumentParser(unittest.TestCase):
    def test_comma_separated(self):
        args = self.parse_arguments_set_defaults(
            ['-f', 'my_midi.mid', '-s', '1,2,3', '-a', '4', '-t', '7,8'])
        self.assertEqual(args.file_path, 'my_midi.mid')
        self.assertEqual(len(args.soprano), 3)
        self.assertCountEqual(args.soprano, [1, 2, 3])
        self.assertEqual(len(args.alto), 1)
        self.assertCountEqual(args.alto, [4])
        self.assertEqual(len(args.tenor), 2)
        self.assertCountEqual(args.tenor, [7, 8])
        self.assertEqual(args.bass, None)

    def parse_arguments_set_defaults(self, argument_list: List[str]
                                     ) -> argparse.Namespace:
        parser = midi_to_part_mp3s.get_parser()
        args = parser.parse_args(argument_list)
        midi_to_part_mp3s.set_defaults(args)
        return args


if __name__ == '__main__':
    unittest.main()
