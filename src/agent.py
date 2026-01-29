import json

from typing import Any

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.columns import Columns

from tools import FUNCTIONS, FUNCTION_MAP, SAFE_FUNCTIONS
from data import Data

console = Console()

def ask_calling(tool_name: str, tool_args: dict[str, Any]) -> bool:
    print('\033[1F\033[2K', end='')
    
    strargs = {}
    for key, value in tool_args.items():
        strargs[key] = value if len(value) < 50 else value[47] + '...'
    
    calling_str = f'[bold cyan]{tool_name}[/bold cyan] [gray42]{strargs}`[/gray42]'
    
    if tool_name not in SAFE_FUNCTIONS:
        print()
        console.print(calling_str)
        accept = console.input('Accept? (y/n): ').lower() == 'y'
                    
        print('\033[1F\033[2K\033[1F\033[2K\033[1F\033[2K', end='')
                    
        if not accept:
            console.print('[red]✗[/red] ' + calling_str)
            return False
                
    console.print('[green]✓[/green] ' + calling_str)
    return True

def send_message(data: Data) -> tuple[list[Messages], int]:
    spinner = Spinner('dots', style='color(140)')
    
    usage = 0
    
    while True:
        chat = Chat(messages=data.messages,
                    functions=FUNCTIONS)
            
        stream = data.client.stream(chat)

        full_content = ''
        pending_function_call = None
        
        with Live(console=console, refresh_per_second=12, vertical_overflow="visible") as live:
            live.update(Columns([spinner, '[bold] Thinking[/bold]']))
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                
                if delta.content and '<|' not in delta.content and '|>' not in delta.content:
                    if not full_content:
                        print()
                    
                    full_content += delta.content
                    live.update(Markdown(full_content))
                
                if delta.function_call:
                    pending_function_call = delta.function_call
                
                if chunk.usage:
                    usage += chunk.usage.total_tokens
            
        if pending_function_call:
            data.messages.append(Messages(
                role=MessagesRole.ASSISTANT,
                content=full_content,
                function_call=pending_function_call
            ))
            
            func_call = pending_function_call
            
            name = func_call.name
            args = func_call.arguments or {}
                    
            if not ask_calling(name, args):
                data.messages.append(Messages(
                    role=MessagesRole.FUNCTION,
                    name=name,
                    content=json.dumps({'success': False, 'reason': 'User rejected the function.'})
                ))
                continue
                
            try:
                result = FUNCTION_MAP[func_call.name](**args)
                
                result['success'] = True
            except Exception as e:
                result = {'success': False, 'error': str(e)}
                
            data.messages.append(Messages(
                role=MessagesRole.FUNCTION,
                name=name,
                content=json.dumps(result)
            ))

            continue
        else:
            data.messages.append(Messages(role=MessagesRole.ASSISTANT, content=full_content))
            print()
            return data.messages, usage
