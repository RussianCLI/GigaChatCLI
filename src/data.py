from pathlib import Path

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
    autonomous: bool

dotenv_path = Path.home() / '.gigachat'
