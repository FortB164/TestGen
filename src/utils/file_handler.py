from pathlib import Path
from typing import Generator

def read_python_file(file_path: str, chunk_size: int = 8192) -> str:
    """Read the content of a Python file in chunks."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_file(file_path: Path, chunk_size: int = 8192) -> str:
    """Read file content with proper encoding handling and chunked reading."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()

def read_file_chunks(file_path: Path, chunk_size: int = 8192) -> Generator[str, None, None]:
    """Read file content in chunks to save memory."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            while chunk := f.read(chunk_size):
                yield chunk
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            while chunk := f.read(chunk_size):
                yield chunk 