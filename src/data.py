from pathlib import Path
from typing import Optional

from gigachat import GigaChat
from gigachat import Messages

from rich.console import Console

from dataclasses import dataclass
@dataclass
class Data:
    client: GigaChat
    console: Console
    messages: list[Messages]
    used_tokens: int

dotenv_path = Path.home() / '.gigachat'
