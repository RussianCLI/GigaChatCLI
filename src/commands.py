import os

from rich.table import Table

from dotenv import set_key

from gigachat import GigaChat, Messages, MessagesRole

from prompt import system_prompt
from data import Data, dotenv_path

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
    def __init__(self, data: Data):
        self.data = data
    
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
            
            try:
                return cmd.func(self.data, *args)
            except TypeError as e:
                self.data.console.print(f'[bold][red]Error:[/bold] {e}[/red]')
        
        return 0

@Command('clear', 'reset')
def clear_cmd(data: Data):
    '''clear the terminal and context'''
    
    data.console.clear()
    
    data.messages = [Messages(role=MessagesRole.SYSTEM, content=system_prompt)]
    data.used_tokens = 0

@Command('quit', 'exit')
def quit_cmd(data: Data):
    '''quit from GigaChatCLI'''
    
    data.console.print('[color(135)]Bye-bye![/color(135)]')
    return 1

@Command('model')
def model_cmd(data: Data, *args):
    '''change the model or show the current. model {name}.'''
    
    if not args:
        current_model = os.getenv('GIGACHAT_MODEL') or 'GigaChat'
        data.console.print(f'Current model is [bold color(135)]{current_model}[/bold color(135)]')
        return 0
    
    model = args[0]
    models = [model.id_ for model in data.client.get_models().data]
    
    if model not in models:
        models_str = '\n'.join(models)
        data.console.print(f'[red]No such model![/red] Models available:\n[color(135)]{models_str}[color(135)]')
        return 0
    
    data.client = GigaChat(verify_ssl_certs=False,
                           model=model)
    
    set_key(dotenv_path=dotenv_path,
            key_to_set='GIGACHAT_MODEL',
            value_to_set=model)
    
    data.console.print(f'Successfully changed model to [bold]{model}[/bold] and saved to {dotenv_path}')

@Command('help')
def help_cmd(data: Data):
    '''see the command list'''

    table = Table(show_header=False, box=None)
    table.add_column("Command", justify="left")
    table.add_column("Description", justify="right")

    for cmd in Command.commands:
        aliases = ' (' + ', '.join(cmd.aliases) + ')' if cmd.aliases else ''
        
        namestring = f'[bold][color(140)]{cmd.name}[/bold]{aliases}[/color(140)]'
        docstring = cmd.func.__doc__ if cmd.func.__doc__ else ''
        
        table.add_row(namestring, docstring)
    
    data.console.print(table)
