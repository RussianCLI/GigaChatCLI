import os

from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole

from rich.console import Console

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

from agent import send_message
from commands import Command, CommandParser, clear_cmd
from data import Data, dotenv_path

def main():
    load_dotenv(dotenv_path=dotenv_path)
    
    console = Console(highlight=False)
    client = GigaChat(verify_ssl_certs=False,
                      model=os.getenv('GIGACHAT_MODEL'))
    data = Data(client, console, [], 0)
    
    parser = CommandParser(data)
    
    command_list = []
    for cmd in Command.commands:
        command_list.append(f'/{cmd.name}')
            
    completer = WordCompleter(command_list, ignore_case=True, sentence=True)
    
    style = Style.from_dict({
        'completion-menu.completion': 'bg:default #aaaaaa',
        'completion-menu.completion.current': 'bg:default #af87d7',
        'scrollbar.background': 'bg:default',
        'scrollbar.button': 'bg:default',
    })
    
    session = PromptSession(completer=completer, style=style, complete_while_typing=True)

    clear_cmd(data)
    
    while True:
        data.console.print(f'[gray50]{(data.used_tokens / 1000):.1f}k tokens[/gray50]')

        try:
            user_prompt = session.prompt(HTML('<b><style fg="#af87d7">> </style></b>'))
        except (KeyboardInterrupt, EOFError):
            break

        if not user_prompt.strip():
            continue

        if user_prompt.startswith('/'):
            if parser.parse(user_prompt[1:]):
                break
            else:
                data.console.print()
                continue

        data.messages.append(Messages(role=MessagesRole.USER, content=user_prompt))

        data.messages, used_tokens = send_message(data)

        data.used_tokens += used_tokens

if __name__ == '__main__':
    main()
