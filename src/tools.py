import os
import re
import subprocess

import urllib.request
import urllib.parse

from typing import Any

from gigachat.models import Function, FunctionParameters

write_function = Function(
    name='write',
    description='Запись в файл',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Относительный или абсолютный путь к файлу.'
            },
            'content': {
                'type': 'string',
                'description': 'Новое содержимое файла.'
            }
        },
        required=['path', 'content'],
    ),
)

read_function = Function(
    name='read',
    description='Прочитать содержимое файла',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Относительный или абсолютный путь к файлу.'
            },
        },
        required=['path'],
    ),
)

ls_function = Function(
    name='ls',
    description='Просмотреть содержимое директории',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Относительный или абсолютный путь к директории.'
            },
        },
        required=['path'],
    ),
)

web_search_function = Function(
    name='web_search',
    description='Поиск в интернете',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'query': {
                'type': 'string',
                'description': 'Поисковый запрос.'
            },
        },
        required=['query'],
    ),
)

shell_function = Function(
    name='shell',
    description='Запуск команды в терминале',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'command': {
                'type': 'string',
                'description': 'Команда для выполнения.'
            },
        },
        required=['command'],
    ),
)

def write_tool(path: str, content: str) -> dict[str, Any]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return {'success': True, 'path': path}

def read_tool(path: str) -> dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {'content': content}

def ls_tool(path: str) -> dict[str, Any]:
    files = os.listdir(path)
    
    files_info = {}
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            files_info[file] = 'directory'
        else:
            files_info[file] = 'file'
    
    return {'files': files_info}

def web_search_tool(query: str) -> dict[str, Any]:
    encoded_query = urllib.parse.quote(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded_query}'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ...'}
        
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode('utf-8')

    links = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', html)
    results = []
    for i, (link, title) in enumerate(links[:5]):
        results.append(f"[{i+1}] {title.strip()}\nURL: {link}")
            
    return {'results': '\n\n'.join(results)}

def shell_tool(command: str) -> dict[str, Any]:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    output = result.stdout + (f"\n[stderr]\n{result.stderr}" if result.stderr else "")
    
    return {"success": result.returncode == 0, "output": output or "(no output)", "code": result.returncode}

FUNCTIONS = [
    write_function,
    read_function,
    ls_function,
    web_search_function,
    shell_function
]

FUNCTION_MAP = {
    'write': write_tool,
    'read': read_tool,
    'ls': ls_tool,
    'web_search': web_search_tool,
    'shell': shell_tool,
}
