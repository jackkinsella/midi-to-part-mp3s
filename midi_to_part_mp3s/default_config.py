from midi_to_part_mp3s.custom_types import ConfigType

default_config: ConfigType = {
    "file_path": '',
    "instrument": 0,
    "instrumental_accompaniment": [],
    "instrumental_volume": 2.0,
    "output_directory": "./output",
    "soundfont_path": "./soundfonts/timbres-of-heaven.sf2",
    "verbose": False,
    "voices": {
        "alto": [2],
        "bass": [4],
        "soprano": [1],
        "tenor": [3]
    },
}
