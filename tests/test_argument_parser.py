import context
from midi_to_part_mp3s.cli import parse_and_set_defaults

import unittest
import argparse
from typing import List


class TestArgumentParser(unittest.TestCase):
    def test_comma_separated(self):
        config = parse_and_set_defaults(
            ['-f', 'my_midi.mid', '-s', '1,2,3', '-a', '4', '-t', '7,8'])
        self.assertEqual(config["file_path"], 'my_midi.mid')
        self.assertCountEqual(config["soprano"], [1, 2, 3])
        self.assertCountEqual(config["alto"], [4])
        self.assertCountEqual(config["tenor"], [7, 8])
        self.assertEqual(config["bass"], None)


if __name__ == '__main__':
    unittest.main()
