from gigachat import GigaChat
from rich.console import Console

class Command:
    commands = []
    def __init__(self, name: str, *aliases: str):
        self.name = name
        self.aliases = aliases
        self.func = None
        
        Command.commands.append(self)
    
    def __call__(self, func):
        self.func = func
        return func

class CommandParser:
    def __init__(self, client: GigaChat, console: Console):
        self.client = client
        self.console = console
    
    def parse(self, text: str) -> int:
        '''Parse commands. Returns signals:
        0 - do 'continue'
        1 - do 'break' '''
        
        if not text.strip():
            return 0
        
        raw_cmd = text.strip().split()
        name = raw_cmd[0]
        args = raw_cmd[1:]
        
        for cmd in Command.commands:
            if name != cmd.name and name not in cmd.aliases:
                continue
            
            return cmd.func(self.client, self.console, *args)
        
        return 0
