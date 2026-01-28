from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole

from rich.console import Console

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
    
    load_dotenv()
    
    console = Console(highlight=False)
    client = GigaChat(verify_ssl_certs=False,
                      model='GigaChat-2-Pro')
    
    parser = CommandParser(client, console)

    clear_cmd(client, console)
    
    while True:
        console.print(f'[gray42] {(tokens / 1000):.1f}k tokens[/gray42]')
        user_prompt = console.input('[bold color(135)]> [/bold color(135)]')

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
