import os
import subprocess
import shlex

from typing import Any

from gigachat.models import Function, FunctionParameters
from ddgs import DDGS

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

search_function = Function(
    name='search',
    description='Search the web',
    parameters=FunctionParameters(
        type='object',
        properties={  # type: ignore
            'query': {
                'type': 'string',
                'description': 'Query to search for'
            },
        },
        required=['query'],
    ),
)

mkdir_function = Function(
    name='mkdir',
    description='Create a directory',
    parameters=FunctionParameters(
        type='object',
        properties={ # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path of new directory'
            }
        },
        required=['path'],
    )
)

touch_function = Function(
    name='touch',
    description='Create a file',
    parameters=FunctionParameters(
        type='object',
        properties={ # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path of new file'
            }
        },
        required=['path'],
    )
)

execute_function = Function(
    name='execute',
    description='Execute a command on user\'s computer',
    parameters=FunctionParameters(
        type='object',
        properties={ # type: ignore
            'command': {
                'type': 'string',
                'description': 'Command to execute'
            }
        },
        required=['command'],
    )
)

remove_function = Function(
    name='remove',
    description='Remove the file',
    parameters=FunctionParameters(
        type='object',
        properties={ # type: ignore
            'path': {
                'type': 'string',
                'description': 'Relative or absolute path of file to remove'
            }
        },
        required=['path'],
    )
)

def write_tool(path: str, content: str) -> dict[str, Any]:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return {'path': path}

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

def search_tool(query: str) -> dict[str, Any]:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    
    return {'results': results}

def mkdir_tool(path: str) -> dict[str, Any]:
    os.makedirs(path)
    
    return {'path': path}

def touch_tool(path: str) -> dict[str, Any]:
    with open(path, 'x'):
        pass
    
    return {'path': path}

def execute_tool(command: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            shlex.split(command.strip()),
            capture_output=True,
            text=True,
            check=True
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.CalledProcessError as e:
        return {
            'error': True,
            'returncode': e.returncode,
            'stdout': e.stdout,
            'stderr': e.stderr
        }
    except Exception as e:
        return {
            'error': True,
            'message': str(e)
        }

def remove_tool(path: str) -> dict[str, Any]:
    os.remove(path)

    return {'path': path}

FUNCTIONS = [
    write_function,
    read_function,
    ls_function,
    search_function,
    mkdir_function,
    touch_function,
    execute_function,
    remove_function
]

FUNCTION_MAP = {
    'write': write_tool,
    'read': read_tool,
    'ls': ls_tool,
    'search': search_tool,
    'mkdir': mkdir_tool,
    'touch': touch_tool,
    'execute': execute_tool,
    'remove': remove_tool
}

SAFE_FUNCTIONS = [
    'ls',
    'read',
    'search'
]
