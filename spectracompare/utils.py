# Copyright (c) 2026 Valerio Fuoglio
# Licensed under the MIT License.

import warnings
from mutagen.mp3 import MP3
from rich.console import Console

warnings.filterwarnings("ignore")
console = Console()

def get_bitrate(path: str) -> int:
    audio = MP3(path)
    return audio.info.bitrate
