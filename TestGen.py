import re
import os
import ollama
import json
from typing import List, Dict, Tuple
from pathlib import Path
import argparse

class ModelTrainer:
    def __init__(self, model_name: str = "starcoder:7b"):
        """Initialize the model trainer with a specific Ollama model."""
        self.model_name = model_name
        self.training_data_path = 'training_data'
        
    def prepare_training_data(self, source_dir: str, test_dir: str) -> List[Dict]:
        """
        Prepare training data from source and test files.
        Returns a list of training examples in the format required by Ollama.
        """
        training_examples = []
        
        # Get all Python files from both directories
        source_files = list(Path(source_dir).glob('**/*.py'))
        test_files = list(Path(test_dir).glob('**/*.py'))
        
        # Create a mapping of source files to their test files
        file_pairs = self._match_source_test_files(source_files, test_files)
        
        for source_file, test_file in file_pairs:
            try:
                # Read source and test content
                source_content = self._read_file(source_file)
                test_content = self._read_file(test_file)
                
                # Create training example
                example = {
                    "instruction": "Generate test cases for the following Python function:",
                    "input": source_content,
                    "output": test_content
                }
                training_examples.append(example)
                
            except Exception as e:
                print(f"Error processing {source_file}: {e}")
        
        return training_examples
    
    def _match_source_test_files(self, source_files: List[Path], test_files: List[Path]) -> List[Tuple[Path, Path]]:
        """Match source files with their corresponding test files."""
        file_pairs = []
        
        for source_file in source_files:
            # Try to find matching test file
            test_file = None
            source_name = source_file.stem
            
            # Look for test file with _test suffix
            test_file = next((f for f in test_files if f.stem == f"{source_name}_test"), None)
            
            if test_file:
                file_pairs.append((source_file, test_file))
            else:
                print(f"No matching test file found for {source_file}")
        
        return file_pairs
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with proper encoding handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def save_training_data(self, examples: List[Dict], output_file: str):
        """Save training examples to a JSON file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2)
    
    def fine_tune_model(self, training_data_file: str, output_model_name: str):
        """
        Fine-tune the model using the prepared training data.
        This uses Ollama's fine-tuning capabilities.
        """
        try:
            # Read training data
            with open(training_data_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # Prepare the fine-tuning configuration
            config = {
                "model": self.model_name,
                "output_model": output_model_name,
                "training_data": training_data
            }
            
            # Call Ollama's fine-tuning API
            response = ollama.create(
                model=output_model_name,
                path=training_data_file,
                config=config
            )
            
            print(f"Fine-tuning completed. New model name: {output_model_name}")
            return response
            
        except Exception as e:
            print(f"Error during fine-tuning: {e}")
            raise

class TestGenerator:
    def __init__(self, model_name: str = "starcoder:7b"):
        """Initialize the test generator with a specific Ollama model."""
        self.model_name = model_name
        self.instructions_path = 'instructions.txt'  # Hardcoded instructions path
        self.files_list_path = 'programming_files_list.txt'  # Hardcoded files list path
        self.trainer = ModelTrainer(model_name)  # Add trainer instance

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

def test_functionname_basic_1():
    # Test basic functionality with typical inputs
    assert functionname(typical_input_1) == expected_result_1

def test_functionname_basic_2():
    # Test basic functionality with different typical inputs
    assert functionname(typical_input_2) == expected_result_2

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

ANALYZE THE FUNCTION'S PURPOSE AND PARAMETERS TO GENERATE APPROPRIATE TESTS.
FOR EACH FUNCTION, GENERATE TESTS THAT COVER:

1. test_functionname_basic_1(): Basic functionality with typical inputs
2. test_functionname_basic_2(): Basic functionality with different typical inputs
3. test_functionname_edge_1(): Edge cases (boundary values, empty inputs, etc.)
4. test_functionname_edge_2(): More edge cases specific to the function
5. test_functionname_error_1(): Error cases (invalid inputs, type errors, etc.)
6. test_functionname_error_2(): More error cases specific to the function

WRITE EXACTLY 6 TEST FUNCTIONS FOR EACH SOURCE FUNCTION.
EACH TEST FUNCTION MUST CONTAIN DIFFERENT TEST CASES.
EACH TEST FUNCTION MUST CONTAIN ACTUAL ASSERT STATEMENTS.
START IMMEDIATELY WITH THE FIRST TEST FUNCTION.
DO NOT WRITE ANYTHING ELSE.

EXAMPLE RESPONSES:

For a string manipulation function:
def test_reverse_string_basic_1():
    assert reverse_string("hello") == "olleh"
    assert reverse_string("world") == "dlrow"

def test_reverse_string_basic_2():
    assert reverse_string("python") == "nohtyp"
    assert reverse_string("test") == "tset"

def test_reverse_string_edge_1():
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"

def test_reverse_string_edge_2():
    assert reverse_string("  ") == "  "
    assert reverse_string("123") == "321"

def test_reverse_string_error_1():
    with pytest.raises(TypeError):
        reverse_string(None)
    with pytest.raises(TypeError):
        reverse_string(123)

def test_reverse_string_error_2():
    with pytest.raises(TypeError):
        reverse_string([])
    with pytest.raises(TypeError):
        reverse_string({})

For a mathematical function:
def test_calculate_area_basic_1():
    assert calculate_area(5, 3) == 15
    assert calculate_area(4, 4) == 16

def test_calculate_area_basic_2():
    assert calculate_area(2.5, 2) == 5
    assert calculate_area(3, 3.5) == 10.5

def test_calculate_area_edge_1():
    assert calculate_area(0, 5) == 0
    assert calculate_area(5, 0) == 0

def test_calculate_area_edge_2():
    assert calculate_area(0.1, 0.1) == pytest.approx(0.01)
    assert calculate_area(1e-10, 1e-10) == pytest.approx(1e-20)

def test_calculate_area_error_1():
    with pytest.raises(ValueError):
        calculate_area(-1, 5)
    with pytest.raises(ValueError):
        calculate_area(5, -1)

def test_calculate_area_error_2():
    with pytest.raises(TypeError):
        calculate_area("5", 3)
    with pytest.raises(TypeError):
        calculate_area(5, "3")

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
            test_types = ['basic_1', 'basic_2', 'edge_1', 'edge_2', 'error_1', 'error_2']
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
                    elif test_type.startswith('error'):
                        placeholder = f"""def test_{source_name}_{test_type}():
    # Example error case test
    with pytest.raises(Exception):
        {source_name}(invalid_input)  # Replace with appropriate values"""
                    else:  # basic
                        placeholder = f"""def test_{source_name}_{test_type}():
    # Example basic case test
    assert {source_name}(typical_input_1) == expected_result_1
    assert {source_name}(typical_input_2) == expected_result_2"""
                    
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
    parser = argparse.ArgumentParser(description='Test Generator and Model Trainer')
    parser.add_argument('--mode', choices=['generate', 'train'], default='generate',
                      help='Mode to run in: generate tests or train model')
    parser.add_argument('--source-dir', help='Directory containing source Python files')
    parser.add_argument('--test-dir', help='Directory containing test Python files')
    parser.add_argument('--output-model', help='Name for the fine-tuned model')
    parser.add_argument('--model', default='starcoder:7b',
                      help='Base model to use (default: starcoder:7b)')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        if not all([args.source_dir, args.test_dir, args.output_model]):
            print("Error: --source-dir, --test-dir, and --output-model are required for training mode")
            return
            
        trainer = ModelTrainer(args.model)
        
        # Prepare training data
        print("Preparing training data...")
        examples = trainer.prepare_training_data(args.source_dir, args.test_dir)
        
        if not examples:
            print("No training examples found!")
            return
            
        # Save training data
        training_data_file = 'training_data/training_examples.json'
        trainer.save_training_data(examples, training_data_file)
        print(f"Saved {len(examples)} training examples to {training_data_file}")
        
        # Fine-tune model
        print("Starting model fine-tuning...")
        trainer.fine_tune_model(training_data_file, args.output_model)
        
    else:  # generate mode
        generator = TestGenerator(args.model)
        try:
            generated_test_files = generator.process_files_list()
            print(f"Generated test files: {generated_test_files}")
        except Exception as e:
            print(f"Error generating tests: {e}")

if __name__ == "__main__":
    main()
