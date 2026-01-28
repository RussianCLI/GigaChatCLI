import json

from typing import Any

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

from tools import FUNCTIONS, FUNCTION_MAP, SAFE_FUNCTIONS

console = Console()

def ask_calling(tool_name: str, tool_args: dict[str, Any]) -> bool:
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

def send_message(messages: list[Messages], client: GigaChat) -> tuple[list[Messages], int]:
    spinner = Spinner('dots', text='[color(140)]Waiting for response...[/color(140)]')
    panel = Panel(spinner, border_style='color(140)', title='Agent Status')
    
    while True:
        with Live(panel, refresh_per_second=10, transient=True):
            chat = Chat(messages=messages,
                        functions=FUNCTIONS)
            
            response = client.chat(chat)
        
        choice = response.choices[0]
        message = choice.message
        
        if choice.finish_reason == 'function_call':
            func_call = message.function_call
            if func_call:
                messages.append(message)
                
                name = func_call.name
                args = func_call.arguments or {}
                
                if not ask_calling(name, args):
                    messages.append(Messages(
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
                
                messages.append(Messages(
                    role=MessagesRole.FUNCTION,
                    name=name,
                    content=json.dumps(result)
                ))

                continue
        else:
            messages.append(Messages(role=MessagesRole.ASSISTANT, content=message.content))
            
            print()
            console.print(Markdown(message.content))
            print()
            
            return messages, response.usage.total_tokens
