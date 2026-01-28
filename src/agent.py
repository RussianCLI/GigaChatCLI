import json

from gigachat import GigaChat
from gigachat.models import Chat, ChatCompletion, Messages, MessagesRole

from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.spinner import Spinner
from rich.columns import Columns
from rich.markdown import Markdown

from tools import FUNCTIONS, FUNCTION_MAP
from styling import STYLING

console = Console(theme=STYLING)

def get_chat(messages: list[Messages], client: GigaChat) -> ChatCompletion:
    spinner = Spinner('dots', style='bold color(140)')
    status_content = Columns([spinner, ' Waiting for response...'])
    
    status_panel = Panel(status_content,
                         title='[bold color(140)]Agent Status[/bold color(140)]',
                         border_style='color(140)')
    
    while True:
        chat = Chat(messages=messages, functions=FUNCTIONS)

        with Live(status_panel, console=console, refresh_per_second=10, transient=True):
            response = client.chat(chat)
            
        choice = response.choices[0]
        message = choice.message
        
        messages.append(message)
            
        if choice.finish_reason == 'function_call':
            if message.content:
                print()

                summary = message.content.split('\n')[0]
                if len(summary) > 150: summary = summary[:147] + '...'
                console.print(f'[gray42]󰘦 {summary}[/gray42]')
                
                print()
            
            func_call = message.function_call
            if func_call:
                args = func_call.arguments or {}
                
                str_args = {}
                for key, val in args.items():
                    val = str(val)
                    
                    if len(val) > 30:
                        str_args[key] = val[:27] + '...'
                    else:
                        str_args[key] = val
                
                calling_text = f'[cyan]{func_call.name}[/cyan] [gray27]{str_args}[/gray27]'
                
                console.print()
                
                console.print(calling_text)
                confirm = console.input('[bold]Accept? (y/n): [/bold]').lower()
                
                print('\033[F\033[K\033[F\033[K\033[F\033[K', end='', flush=True)
                        
                if confirm != 'y':
                    console.print(f'[red]✕[/red] ' + calling_text)
                    messages.append(Messages(
                        role=MessagesRole.FUNCTION,
                        name=func_call.name,
                        content=json.dumps({'error': 'User denied execution'})
                    ))
                    continue
                    
                console.print(f'[green]✓[/green] ' + calling_text)
                    
                try:
                    result = FUNCTION_MAP[func_call.name](**args)
                    
                    result['success'] = True
                except Exception as e:
                    result = {'success': False, 'error': str(e)}
                    
                messages.append(Messages(
                    role=MessagesRole.FUNCTION,
                    name=func_call.name,
                    content=json.dumps(result)
                ))

                continue
        else:
            print()

            console.print(Markdown(response.choices[0].message.content))
                
            print()
            
            return response
            break
