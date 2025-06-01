import re
import os
import ollama
from typing import List

class TestGenerator:
    def __init__(self, model_name: str = "mistral"):
        """Initialize the test generator with a specific Ollama model."""
        self.model_name = model_name
        self.instructions_path = 'instructions.txt'  # Hardcoded instructions path
        self.files_list_path = 'programming_files_list.txt'  # Hardcoded files list path

    def read_python_file(self, file_path: str) -> str:
        """
        Read the content of the Python file.
        Returns the content as a string.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def generate_test_cases(self, code: str) -> str:
        """Generate test cases for the entire code using Ollama."""
        # Use the provided prompt from instructions.txt
        prompt = self._read_instructions()
        
        # Extract function names from the code for validation
        function_names = self._extract_function_names(code)
        print(f"Found {len(function_names)} functions to test: {function_names}")
        
        # Try up to 3 times to generate tests
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                generated_tests = self._call_ollama(prompt, code)
                if generated_tests:
                    processed_tests = self._post_process_tests(generated_tests, function_names)
                    
                    # Validate that we have tests for at least some functions
                    if processed_tests and len(processed_tests.strip().splitlines()) > 5:
                        return processed_tests
                    else:
                        print(f"Attempt {attempt+1}: Generated tests were empty or insufficient")
                else:
                    print(f"Attempt {attempt+1}: No tests generated")
                    
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
            
            # Wait a bit before retrying
            if attempt < max_attempts - 1:
                print(f"Retrying test generation (attempt {attempt+2}/{max_attempts})...")
                # Could add a small delay here if needed
        
        # If all attempts failed, return a basic template with imports
        return "import pytest\nimport sys\nimport math\nfrom test import *\n\n# Test generation failed after multiple attempts"

    def _extract_function_names(self, code: str) -> list:
        """Extract function names from the code."""
        function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        function_names = re.findall(function_pattern, code)
        
        # Process function names to handle special cases
        processed_names = []
        for name in function_names:
            # Handle functions like 'sum_of_list' -> 'sum_of'
            if name.startswith('sum_of_'):
                processed_names.append('sum_of')
            # Handle functions like 'average_of_list' -> 'average_of'
            elif name.startswith('average_of_'):
                processed_names.append('average_of')
            else:
                processed_names.append(name)
                
        return processed_names

    def _read_instructions(self) -> str:
        """Read the instructions from the hardcoded file path."""
        with open(self.instructions_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _call_ollama(self, prompt: str, code: str) -> str:
        """Call Ollama API to generate test cases based on the entire code."""
        try:
            # Extract function names for better examples
            function_names = self._extract_function_names(code)
            
            # Create examples based on actual functions in the code
            examples = ""
            if function_names:
                example_func = function_names[0]
                examples = f"""
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
            
            # Prepare the message with clear formatting instructions and better examples
            message = f"""WRITE ONLY PYTHON TEST FUNCTIONS IN THIS EXACT FORMAT:

def test_functionname_edge_1():
    # Test boundary values, minimum values
    assert functionname(min_value) == expected_result
    
def test_functionname_edge_2():
    # Test boundary values, maximum values
    assert functionname(max_value) == expected_result
    
def test_functionname_null_1():
    # Test None values or empty inputs
    with pytest.raises(TypeError):
        functionname(None)
    
def test_functionname_null_2():
    # Test invalid types or formats
    with pytest.raises(ValueError):
        functionname(invalid_input)
    
def test_functionname_unusual_1():
    # Test very large values
    assert functionname(very_large_value) == expected_result
    
def test_functionname_unusual_2():
    # Test unusual inputs like negative numbers or special characters
    assert functionname(unusual_input) == expected_result

{examples}

IMPORTANT: EACH TEST FUNCTION MUST HAVE DIFFERENT TEST CASES!
DO NOT DUPLICATE TEST CASES ACROSS DIFFERENT TEST FUNCTIONS!
DO NOT CREATE PLACEHOLDER FUNCTIONS - IMPLEMENT ACTUAL TESTS!

{prompt}

Here is the code to test:

{code}"""
            
            # Call Ollama API with more specific instructions
            response = ollama.chat(model=self.model_name, messages=[
                {"role": "system", "content": """IMPORTANT: YOU ARE A TEST GENERATOR BOT.
YOUR ONLY PURPOSE IS TO WRITE PYTHON TEST FUNCTIONS WITH ACTUAL ASSERTIONS.
DO NOT WRITE PLACEHOLDER FUNCTIONS OR TODO COMMENTS.
IF YOU WRITE ANYTHING ELSE, YOU WILL BE PENALIZED.
IF YOU PROVIDE SUGGESTIONS OR EXPLANATIONS, YOU WILL BE PENALIZED.
IF YOU USE MARKDOWN CODE BLOCKS, YOU WILL BE PENALIZED.

YOU MUST FOLLOW THIS EXACT NAMING PATTERN FOR EACH FUNCTION:
1. test_functionname_edge_1() - Test edge case 1 (e.g., boundary values, minimum values)
2. test_functionname_edge_2() - Test edge case 2 (e.g., boundary values, maximum values)
3. test_functionname_null_1() - Test null case 1 (e.g., None, empty strings)
4. test_functionname_null_2() - Test null case 2 (e.g., invalid types)
5. test_functionname_unusual_1() - Test unusual case 1 (e.g., very large values)
6. test_functionname_unusual_2() - Test unusual case 2 (e.g., very small values)

WRITE EXACTLY 6 TEST FUNCTIONS FOR EACH SOURCE FUNCTION.
EACH TEST FUNCTION MUST CONTAIN DIFFERENT TEST CASES.
EACH TEST FUNCTION MUST CONTAIN ACTUAL ASSERT STATEMENTS.
START IMMEDIATELY WITH THE FIRST TEST FUNCTION.
DO NOT WRITE ANYTHING ELSE.

EXAMPLE RESPONSE:
def test_add_edge_1():
    assert add(0, 0) == 0
    assert add(1, 0) == 1

def test_add_edge_2():
    assert add(-1, 1) == 0
    assert add(sys.maxsize, 0) == sys.maxsize

def test_add_null_1():
    with pytest.raises(TypeError):
        add(None, 5)

def test_add_null_2():
    with pytest.raises(TypeError):
        add("string", 5)

def test_add_unusual_1():
    assert add(-sys.maxsize, 1) == -sys.maxsize + 1

def test_add_unusual_2():
    assert add(0.1, 0.2) == pytest.approx(0.3)

REMEMBER: ONLY WRITE TEST FUNCTIONS WITH ACTUAL ASSERTIONS. NO PLACEHOLDERS OR TODOS."""},
                {"role": "user", "content": message}
            ], options={"temperature": 0.2})  # Slightly higher temperature for more creativity with test cases
            
            # Debug output
            print("Raw Ollama response:", response)
            print("Response type:", type(response))
            
            # Handle ChatResponse type
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                content = response.message.content
            else:
                print("Error: Invalid response format from Ollama")
                return ""
            
            # Remove any text before the first def test_ and after the last line of code
            content = re.sub(r'^.*?(?=def test_)', '', content, flags=re.DOTALL)
            content = re.sub(r'```.*$', '', content, flags=re.DOTALL)
            
            if not content:
                print("Error: Empty content in Ollama response")
                return ""
                
            print(f"Generated {len(content.splitlines())} lines of test code")
            print("First 200 characters of content:", content[:200])
            return content
            
        except Exception as e:
            print(f"Error calling Ollama API: {e}")
            raise  # Re-raise to allow retry logic in generate_test_cases
            
    def _post_process_tests(self, test_code: str, function_names: list) -> str:
        """Clean up and validate generated test code."""
        print("\nDEBUG: Starting post-processing")
        print("Raw test code:", test_code[:200])
        
        # First, try to extract code from code blocks
        code_blocks = re.findall(r'```python\n(.*?)```', test_code, re.DOTALL)
        if code_blocks:
            test_code = code_blocks[0]  # Use the first code block
            print("Found code block:", test_code[:200])
        
        # Split into lines and filter out any lines that don't look like code
        lines = []
        for line in test_code.splitlines():
            # Skip any line that doesn't look like Python code
            if not line.strip():
                continue
            if not (line.strip().startswith('def test_') or 
                   line.strip().startswith('assert') or 
                   line.strip().startswith('with') or
                   line.strip().startswith('#')):
                continue
            lines.append(line)
        
        print(f"DEBUG: Found {len(lines)} lines after filtering")
        
        # Extract all test function definitions
        test_functions = []
        current_func = []
        in_function = False
        
        # Track functions for each source function
        source_functions = {}
        
        # Process the filtered lines
        for line in lines:
            # Start of a new function
            if line.strip().startswith('def test_'):
                if current_func:
                    func_content = '\n'.join(current_func)
                    test_functions.append(func_content)
                    
                    # Extract source function name from the test function name
                    match = re.match(r'def test_([a-zA-Z0-9_]+)_', current_func[0])
                    if match:
                        source_name = match.group(1)
                        if source_name not in source_functions:
                            source_functions[source_name] = []
                        source_functions[source_name].append(func_content)
                
                current_func = [line.strip()]  # Remove any leading/trailing whitespace
                in_function = True
            # Inside a function
            elif in_function and line.strip():
                # Ensure proper indentation (4 spaces) for function body
                if not line.strip().startswith('def '):
                    line = '    ' + line.strip()
                current_func.append(line)
        
        # Add the last function if any
        if current_func:
            func_content = '\n'.join(current_func)
            test_functions.append(func_content)
            
            # Extract source function name from the test function name
            match = re.match(r'def test_([a-zA-Z0-9_]+)_', current_func[0])
            if match:
                source_name = match.group(1)
                if source_name not in source_functions:
                    source_functions[source_name] = []
                source_functions[source_name].append(func_content)
        
        print(f"DEBUG: Found {len(test_functions)} test functions")
        print(f"DEBUG: Found tests for {len(source_functions)} source functions")
        
        # Validate that we have tests for the expected functions
        for func_name in function_names:
            if func_name not in source_functions:
                print(f"WARNING: No tests generated for function '{func_name}'")
        
        # Add necessary imports
        imports = "import pytest\nimport sys\nimport math\nfrom test import *\n\n"
        
        # Process each source function's tests to ensure they're unique
        final_tests = []
        for source_name, funcs in source_functions.items():
            # Ensure we have exactly 6 test functions per source function
            test_types = ['edge_1', 'edge_2', 'null_1', 'null_2', 'unusual_1', 'unusual_2']
            processed_funcs = {}
            
            # Group functions by test type
            for func in funcs:
                for test_type in test_types:
                    if f"test_{source_name}_{test_type}" in func:
                        # Only add if it has actual assertions (not just a placeholder)
                        if 'assert' in func or 'pytest.raises' in func:
                            processed_funcs[test_type] = func
                        break
            
            # Add the processed functions in the correct order
            for test_type in test_types:
                if test_type in processed_funcs:
                    final_tests.append(processed_funcs[test_type])
                else:
                    # Create a more useful placeholder function with example assertions
                    if test_type.startswith('edge'):
                        placeholder = f"""def test_{source_name}_{test_type}():
    # Example edge case test
    assert {source_name}(0) == 0  # Replace with appropriate values
    assert {source_name}(1) == 1  # Replace with appropriate values"""
                    elif test_type.startswith('null'):
                        placeholder = f"""def test_{source_name}_{test_type}():
    # Example null case test
    with pytest.raises(TypeError):
        {source_name}(None)  # Replace with appropriate values"""
                    else:  # unusual
                        placeholder = f"""def test_{source_name}_{test_type}():
    # Example unusual case test
    assert {source_name}(1000) == 1000  # Replace with appropriate values
    assert {source_name}(-1000) == -1000  # Replace with appropriate values"""
                    
                    final_tests.append(placeholder)
                    print(f"WARNING: Missing test type '{test_type}' for function '{source_name}', added example placeholder")
        
        # Combine all tests
        all_tests = imports + "\n\n".join(final_tests)
        
        # Validate the final output
        if not final_tests:
            print("ERROR: No valid test functions generated")
            return imports + "# No valid test functions were generated"
        
        return all_tests

    def process_file(self, file_path: str) -> str:
        """Process a single Python file and generate a test file for it."""
        # Read the source file
        code = self.read_python_file(file_path)
        
        # Generate test cases
        test_content = self.generate_test_cases(code)
        
        # Create test file path by inserting _test before .py
        base, ext = os.path.splitext(file_path)
        test_file_path = f"{base}_test{ext}"
        
        # Get the module name for importing
        module_name = os.path.basename(base)
        
        # Add the import statement for the specific module
        test_content = test_content.replace("from test import *", f"from {module_name} import *")
        
        print(f"Writing test content to {test_file_path}")
        print(f"Test content length: {len(test_content)}")
        try:
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
                f.flush()
                os.fsync(f.fileno())  # Ensure content is written to disk
        except Exception as e:
            print(f"Error writing test file: {e}")
            raise

        return test_file_path

    def process_files_list(self) -> List[str]:
        """
        Process all Python files listed in `programming_files_list.txt`.
        For each file, generate a corresponding test file.
        Returns a list of paths to the generated test files.
        """
        test_files = []

        # Read the list of file paths
        with open(self.files_list_path, 'r', encoding='utf-8') as f:
            file_paths = f.readlines()

        # Process each file in the list
        for file_path in file_paths:
            file_path = file_path.strip()  # Remove any extra spaces or newlines
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

def main():
    """CLI entry point for processing multiple files and generating tests."""
    generator = TestGenerator()
    try:
        generated_test_files = generator.process_files_list()
        print(f"Generated test files: {generated_test_files}")
    except Exception as e:
        print(f"Error generating tests: {e}")

if __name__ == "__main__":
    main()
