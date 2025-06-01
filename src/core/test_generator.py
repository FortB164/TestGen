import re
import os
import ollama
from typing import List, Generator
from ..utils.code_parser import extract_function_names
from ..utils.file_handler import read_python_file
from ..config.settings import INSTRUCTIONS_PATH, FILES_LIST_PATH

class TestGenerator:
    def __init__(self, model_name: str = "starcoder:7b"):
        """Initialize the test generator with a specific Ollama model."""
        self.model_name = model_name
        self.instructions_path = INSTRUCTIONS_PATH
        self.files_list_path = FILES_LIST_PATH
        self._cached_instructions = None  # Cache for instructions

    def _read_instructions(self) -> str:
        """Read the instructions from the hardcoded file path with caching."""
        if self._cached_instructions is None:
            self._cached_instructions = read_python_file(self.instructions_path)
        return self._cached_instructions

    def generate_test_cases(self, code: str) -> str:
        """Generate test cases for the entire code using Ollama."""
        prompt = self._read_instructions()
        function_names = extract_function_names(code)
        print(f"Found {len(function_names)} functions to test: {function_names}")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                generated_tests = self._call_ollama(prompt, code, function_names)
                if generated_tests:
                    processed_tests = self._post_process_tests(generated_tests, function_names)
                    if processed_tests and len(processed_tests.strip().splitlines()) > 5:
                        return processed_tests
                    else:
                        print(f"Attempt {attempt+1}: Generated tests were empty or insufficient")
                else:
                    print(f"Attempt {attempt+1}: No tests generated")
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
            
            if attempt < max_attempts - 1:
                print(f"Retrying test generation (attempt {attempt+2}/{max_attempts})...")
        
        return "import pytest\nimport sys\nimport math\nfrom test import *\n\n# Test generation failed after multiple attempts"

    def _call_ollama(self, prompt: str, code: str, function_names: list) -> str:
        """Call Ollama API to generate test cases with optimized prompt construction."""
        try:
            # Use a generator for examples to save memory
            examples = self._generate_examples(function_names)
            
            # Construct message efficiently
            message = (
                "WRITE ONLY PYTHON TEST FUNCTIONS IN THIS EXACT FORMAT:\n\n"
                "def test_functionname_basic_1():\n"
                "    # Test basic functionality with typical inputs\n"
                "    assert functionname(typical_input_1) == expected_result_1\n\n"
                "def test_functionname_basic_2():\n"
                "    # Test basic functionality with different typical inputs\n"
                "    assert functionname(typical_input_2) == expected_result_2\n\n"
                "def test_functionname_edge_1():\n"
                "    # Test boundary values, minimum values\n"
                "    assert functionname(min_value) == expected_result\n\n"
                "def test_functionname_edge_2():\n"
                "    # Test boundary values, maximum values\n"
                "    assert functionname(max_value) == expected_result\n"
            )
            
            # Combine prompt parts efficiently
            full_prompt = f"{prompt}\n\n{message}\n\n{examples}\n\nNow generate test cases for this code:\n\n{code}"
            
            # Use streaming for large responses
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                stream=True
            )
            
            # Collect response chunks
            result = []
            for chunk in response:
                if 'response' in chunk:
                    result.append(chunk['response'])
            
            return ''.join(result)
            
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None

    def _generate_examples(self, function_names: list) -> str:
        """Generate examples using a memory-efficient approach."""
        if not function_names:
            return ""
            
        example_func = function_names[0]
        return f"""
Here are examples of good test functions for a function named '{example_func}':

def test_{example_func}_edge_1():
    # Test minimum values
    assert {example_func}(0) == 0
    assert {example_func}(1) == 1

def test_{example_func}_edge_2():
    # Test maximum values
    assert {example_func}(100) == 100
    assert {example_func}(-1) == -1

def test_{example_func}_null_1():
    # Test empty or None inputs
    with pytest.raises(TypeError):
        {example_func}(None)

def test_{example_func}_null_2():
    # Test invalid types
    with pytest.raises(TypeError):
        {example_func}("string")

def test_{example_func}_unusual_1():
    # Test very large values
    assert {example_func}(10000) == 10000

def test_{example_func}_unusual_2():
    # Test unusual inputs
    assert {example_func}(-100) == -100
"""

    def _post_process_tests(self, test_code: str, function_names: list) -> str:
        """Clean up and validate generated test code with optimized string operations."""
        if not test_code:
            return None
            
        # Use a list for efficient string concatenation
        parts = []
        
        # Add imports if missing
        if 'import pytest' not in test_code:
            parts.append('import pytest\n')
        if 'import sys' not in test_code:
            parts.append('import sys\n')
        if 'import math' not in test_code:
            parts.append('import math\n')
            
        # Remove markdown code block markers and add the rest
        cleaned_code = re.sub(r'```python\n|```\n', '', test_code)
        parts.append(cleaned_code)
        
        return ''.join(parts)

    def process_file(self, file_path: str) -> str:
        """Process a single Python file and generate a test file for it."""
        code = read_python_file(file_path)
        test_content = self.generate_test_cases(code)
        
        base, ext = os.path.splitext(file_path)
        test_file_path = f"{base}_test{ext}"
        module_name = os.path.basename(base)
        
        # Optimize string replacement
        test_content = test_content.replace("from test import *", f"from {module_name} import *")
        
        print(f"Writing test content to {test_file_path}")
        print(f"Test content length: {len(test_content)}")
        
        try:
            # Use buffered writing for better performance
            with open(test_file_path, 'w', encoding='utf-8', buffering=8192) as f:
                f.write(test_content)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            print(f"Error writing test file: {e}")
            raise

        return test_file_path

    def process_files_list(self) -> List[str]:
        """Process all Python files listed in the files list using generators."""
        test_files = []
        
        # Use a generator to read files
        def file_path_generator():
            with open(self.files_list_path, 'r', encoding='utf-8') as f:
                for line in f:
                    yield line.strip()
        
        for file_path in file_path_generator():
            if os.path.exists(file_path):
                try:
                    test_file = self.process_file(file_path)
                    test_files.append(test_file)
                    print(f"Generated test file: {test_file}")
                except Exception as e:
                    print(f"Error generating test file for {file_path}: {e}")
            else:
                print(f"File not found: {file_path}")

        return test_files 