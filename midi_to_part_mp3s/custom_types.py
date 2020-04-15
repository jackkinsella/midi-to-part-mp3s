from mypy_extensions import TypedDict
from typing_extensions import Literal
from typing import List

SATB_VOICES = ["alto", "soprano", "bass", "tenor"]

# FIXME: I wish I did not have to list these keys once here and then again in
# the VoicesObjectType
VoiceStringsType = Literal["alto", "alto2", "bass",
                           "bass2", "soprano", "soprano2", "tenor", "tenor2"]

VoicesObjectType = TypedDict('VoicesObjectType', {
    'alto': List[int],
    'alto2': List[int],
    'bass': List[int],
    'bass2': List[int],
    'soprano': List[int],
    'soprano2': List[int],
    'tenor': List[int],
    'tenor2': List[int]
})


MidiMessageType = Literal['note_on', 'control_change']
MidiAttribute = Literal['velocity', 'value']

ConfigType = TypedDict('ConfigType', {
    "accompaniment_volume_ratio": float,
    'compress_dynamic_range': bool,
    'file_path': str,
    "generate_accompaniment_tracks": bool,
    "generate_all_but_one_tracks": bool,
    'instrument': int,
    'instrumental_accompaniment': List[int],
    'instrumental_volume': float,
    'log_all_midi_messages': bool,
    'retain_intermediate_files': bool,
    'tempo_scaling_factor': float,
    "output_directory": str,
    'soundfont_path': str,
    'verbose': bool,
    'voices': VoicesObjectType}
)
