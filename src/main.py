import os

from pathlib import Path

from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole

from rich.console import Console

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from agent import send_message
from commands import Command, CommandParser
from prompt import system_prompt

tokens = 0
messages = []
@Command('clear', 'reset')
def clear_cmd(client: GigaChat, console: Console):
    global messages, tokens
    
    messages = [Messages(role=MessagesRole.SYSTEM, content=system_prompt)]
    tokens = 0

@Command('quit', 'exit')
def quit_cmd(client: GigaChat, console: Console):
    console.print('[cyan]Bye-bye![/cyan]')
    return 1

def main():
    global messages, tokens
    
    load_dotenv(dotenv_path=Path.home() / '.gigachat')
    
    console = Console(highlight=False)
    client = GigaChat(verify_ssl_certs=False,
                      model=os.getenv('GIGACHAT_MODEL'))
    
    parser = CommandParser(client, console)
    session = PromptSession()

    clear_cmd(client, console)
    
    while True:
        console.print(f'[gray42] {(tokens / 1000):.1f}k tokens[/gray42]')
        try:
            user_prompt = session.prompt(HTML('<b><style fg="#af87d7">> </style></b>'))
        except (KeyboardInterrupt, EOFError):
            break

        if user_prompt.startswith('/'):
            if parser.parse(user_prompt[1:]):
                break
            else:
                continue
        
        messages.append(Messages(role=MessagesRole.USER, content=user_prompt))
        
        messages, used_tokens = send_message(messages, client)
        
        tokens += used_tokens

if __name__ == '__main__':
    main()
