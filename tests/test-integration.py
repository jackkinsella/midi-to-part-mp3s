import unittest
import os
import shutil

output_directory = "./output"

class TestIntegration(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(output_directory)

    def test_conversion_of_midi(self):
        # TODO: Clean up between tests
        midi_file_path = "./tests/fixtures/Schubert-872-sanctus.mid"
        cmd = "./midi-to-part-mp3s {} -s 0 -a 1 -t 2 -b 3".format(midi_file_path)
        os.system(cmd)

        all_parts_mp3_output = "./output/alle.mp3"
        self.assertTrue(os.path.isfile(all_parts_mp3_output))

if __name__ == '__main__':
    unittest.main()
