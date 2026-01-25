import json

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from tools import FUNCTIONS, FUNCTION_MAP

def get_chat(chat: Chat, client: GigaChat) -> Chat:
    messages = chat.messages.copy()
    
    while True:
        chat = Chat(messages=messages, functions=FUNCTIONS)
        
        response = client.chat(chat)
        
        choice = response.choices[0]
        message = choice.message
        
        if choice.finish_reason == 'function_call':
            func_call = message.function_call
            if func_call:
                messages.append(message)
                
                args = func_call.arguments or {}
                try:
                    result = FUNCTION_MAP[func_call.name](**args)
                    
                    result['success'] = True
                except Exception as e:
                    result = {'success': False, 'error': str(e)}
                
                messages.append(Messages(
                    role=MessagesRole.FUNCTION,
                    name=func_call.name,
                    content=json.dumps({func_call.name: result})
                ))
                
                print(f'func call: {func_call.name}')
                print(f'func returned {result}')

                continue
        else:
            messages.append(Messages(role=MessagesRole.ASSISTANT, content=message.content))
            return Chat(messages=messages)
            break