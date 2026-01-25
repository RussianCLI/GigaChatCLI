import os

from typing import Any

from gigachat.models import Function, FunctionParameters

write_function = Function(
    name='write',
    description='Write to a file',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path to the file to write.'
            },
            'content': {
                'type': 'string',
                'description': 'Content to write to the file.'
            }
        },
        required=['path', 'content'],
    ),
)

read_function = Function(
    name='read',
    description='Read a file',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path to the file to read.'
            },
        },
        required=['path'],
    ),
)

ls_function = Function(
    name='ls',
    description='List files in a directory',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path of directory to list. Pass "." to list current directory.'
            },
        },
        required=['path'],
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

FUNCTIONS = [
    write_function,
    read_function,
    ls_function
]

FUNCTION_MAP = {
    'write': write_tool,
    'read': read_tool,
    'ls': ls_tool
}