from mypy_extensions import TypedDict
from typing_extensions import Literal
from typing import List

VoiceStringsType = Literal["alto", "bass", "soprano", "tenor"]

VoicesObjectType = TypedDict('VoicesObjectType', {
    'alto': List[int],
    'bass': List[int],
    'soprano': List[int],
    'tenor': List[int]
})

ConfigType = TypedDict('ConfigType', {
    "accompaniment_volume_ratio": float,
    'compress_dynamic_range': bool,
    'file_path': str,
    "generate_accompaniment_tracks": bool,
    "generate_all_but_one_tracks": bool,
    'instrument': int,
    'instrumental_accompaniment': List[int],
    'instrumental_volume': float,
    "output_directory": str,
    'soundfont_path': str,
    'verbose': bool,
    'voices': VoicesObjectType})
