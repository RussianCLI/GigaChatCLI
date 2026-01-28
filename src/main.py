import os

from pathlib import Path

from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from rich.console import Console

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PtStyle

from agent import get_chat
from tools import FUNCTIONS

system_prompt = f'''
# РОЛЬ
Ты — автономный инженерный AI-агент. Твоя задача — давать ИСЧЕРПЫВАЮЩИЕ ответы, основанные на ПОЛНОМ анализе кода.

# ПРИМЕР ПРАВИЛЬНОГО ПОВЕДЕНИЯ (FEW-SHOT)
User: "Что делает код в папке utils?"
Agent: (Вызывает ls path="utils")
System: "file1.py file2.py"
Agent: (Вызывает read path="utils/file1.py")
System: "content of file1..."
Agent: (Вызывает read path="utils/file2.py")
System: "content of file2..."
Agent: "Код в папке utils состоит из двух модулей. File1 отвечает за X, а File2 делает Y..."

# АЛГОРИТМ РАБОТЫ
1. **LS**: Если нужно узнать структуру, сделай `ls`.
2. **READ (LOOP)**: Если ты видишь файлы кода, ты ОБЯЗАН прочитать их содержимое. Вызывай `read` для каждого важного файла.
3. **ANSWER**: Только когда тексты файлов у тебя в контексте — отвечай.

# ЗАПРЕТЫ
- ЗАПРЕЩЕНО отвечать, не прочитав файлы.
- ЗАПРЕЩЕНО гадать по названиям ("возможно", "вероятно").
- ЗАПРЕЩЕНО останавливаться на `ls`.

# ИНФОРМАЦИЯ
Рабочая директория: {os.getcwd()}
'''

def main():
    load_dotenv(dotenv_path=Path.home() / '.gigachat_env')
    client = GigaChat(verify_ssl_certs=False,
                      model='GigaChat-2-Max')
    
    messages = []
    messages.append(Messages(role=MessagesRole.SYSTEM, content=system_prompt))

    console = Console(highlight=False)

    history = InMemoryHistory()
    pt_style = PtStyle.from_dict({
        'prompt': 'bold #af87ff',
    })

    token_count = 0
    while True:
        status = f'[gray42]{(token_count / 1000):.1f}k tokens[/gray42]'
        console.print(status)
        
        userprompt = prompt('> ', style=pt_style, history=history)

        if userprompt.lower() in ('exit', 'quit', '/exit', '/quit'):
            break
        
        messages.append(Messages(role=MessagesRole.USER, content=userprompt))
        
        chatcompletion = get_chat(messages, client)
        
        token_count += chatcompletion.usage.total_tokens

if __name__ == '__main__':
    main()
