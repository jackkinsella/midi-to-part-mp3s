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
    'file_path': str,
    'instrument': int,
    'instrumental_accompaniment': List[int],
    'instrumental_volume': float,
    "output_directory": str,
    'soundfont_path': str,
    'verbose': bool,
    'voices': VoicesObjectType})
