import os

from dotenv import load_dotenv

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from agent import get_chat
from tools import FUNCTIONS

load_dotenv()
client = GigaChat(verify_ssl_certs=False)

messages = []

system_prompt = f'''
Ты — автономный исполнитель. Тебе доступны инструменты для выполнения задач.

Твой протокол:
1. Анализ: Если в запросе недостаточно данных для выполнения, используй инструменты поиска/инспекции (ls, поиск, get и т.д.).
2. Точность: При передаче аргументов в инструменты используй ТОЧНЫЕ значения из ответов предыдущих инструментов. Никаких правок и сокращений.
3. Рекурсия: Если инструмент вернул ошибку, проанализируй её, исправь аргументы и попробуй снова.
4. Финал: Когда задача выполнена, дай краткий ответ.

Текущий контекст: {os.getcwd()}
'''

messages.append(Messages(role=MessagesRole.SYSTEM, content=system_prompt))

while True:
    userprompt = input('> ')
    if userprompt.lower() in ('exit', 'quit', '/exit', '/quit'):
        break
    
    messages.append(Messages(role=MessagesRole.USER, content=userprompt))
    
    chat = Chat(
        messages=messages,
        functions=FUNCTIONS
    )
    
    chat = get_chat(chat, client)
    
    messages = chat.messages
    
    print(messages[-1].content)
