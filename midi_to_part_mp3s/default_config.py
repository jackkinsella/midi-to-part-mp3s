from midi_to_part_mp3s.custom_types import ConfigType

default_config: ConfigType = {
    "accompaniment_volume_ratio": 0.28,
    "compress_dynamic_range": True,
    "file_path": '',
    "generate_accompaniment_tracks": True,
    "generate_all_but_one_tracks": False,
    "instrument": 0,
    "instrumental_accompaniment": [],
    "instrumental_volume": 2.0,
    "log_all_midi_messages": False,
    "tempo_scaling_factor": 1.0,
    "retain_intermediate_files": False,
    "output_directory": "./output",
    "soundfont_path": "./soundfonts/timbres-of-heaven.sf2",
    "verbose": False,
    "voices": {
        "alto": [2],
        "alto2": [],
        "bass": [4],
        "bass2": [],
        "soprano": [1],
        "soprano2": [],
        "tenor": [3],
        "tenor2": []
    },
}
