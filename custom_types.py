from mypy_extensions import TypedDict
from typing_extensions import Literal
from typing import List

VoiceStringsType = Literal["alto", "bass", "soprano", "tenor"]

ConfigType = TypedDict('ConfigType', {
    'alto': List[int],
    'bass': List[int],
    'file_path': str,
    'instrument': int,
    'instrumental_accompaniment': List[int],
    'instrumental_volume': float,
    "output_directory": str,
    'soprano': List[int],
    'soundfont_path': str,
    'tenor': List[int]
})
