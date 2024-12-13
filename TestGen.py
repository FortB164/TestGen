from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import re

# Load the CodeGen model
model_name = "Salesforce/codegen-350M-mono"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def extract_functions(code):
    """
    Extract function names from Python code, including multiline definitions.
    """
    pattern = re.compile(r"def (\w+)\(.*\):")
    return pattern.findall(code)

def extract_function_code(code, function_name):
    """
    Extract the full code of a specific function by name, handling nested and multiline functions.
    """
    pattern = re.compile(
        rf"(def {function_name}\(.*\):\n(?:[ \t]+.*\n?)*)",
        re.MULTILINE | re.DOTALL
    )
    match = pattern.search(code)
    return match.group(0) if match else ""

def extract_function_purpose(code, function_name):
    """
    Extract the purpose or description of a function based on its docstring or code context.
    """
    func_code = extract_function_code(code, function_name)
    docstring_match = re.search(r'"""(.*?)"""', func_code, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    return "No description available."

def reformat_test_code(test_code):
    """
    Reformat the generated test code to fix indentation issues.
    """
    try:
        lines = test_code.splitlines()
        processed_lines = [line.rstrip() for line in lines if line.strip()]
        return "\n".join(processed_lines)
    except Exception as e:
        print(f"Error reformatting test code: {e}")
        return test_code

def sanitize_function_name(function_name):
    """
    Ensure the function name is safe for use in test case names.
    """
    return re.sub(r'\W|^(?=\d)', '_', function_name)  # Replace non-alphanumeric characters with '_'

def generate_test_case(function_name, function_purpose):
    """
    Generate test cases for a single function using the model.
    """
    sanitized_name = sanitize_function_name(function_name)
    prompt = f"""
# Write exactly **8 valid and distinct Python test functions** using `pytest` for the function '{function_name}'.
# The function's purpose is: {function_purpose} (or "No description available" if unknown).
#
# Requirements for the generated test functions:
# 1. Each test function must start with 'def test_<function_name>_<scenario>():'.
# 2. Include a concise docstring describing the test's purpose.
# 3. Use Python's `assert` statement to validate the function's behavior.
# 4. Include **exactly 8 distinct and logically meaningful test cases** covering:
#    - 2 typical input scenarios with expected outputs.
#    - 2 edge cases (e.g., empty inputs, boundary values, extreme cases).
#    - 2 invalid inputs (e.g., wrong data types), using `pytest.raises` for exceptions.
#    - 2 additional cases to test performance, rare cases, or other specific conditions.
# 5. Avoid redundant, incomplete, or placeholder test cases.
# 6. Ensure all test cases are runnable, syntactically correct, and logically valid.
# 7. Do not repeat the function's implementation within the test cases.
# 8. Ensure no overlapping function definitions; each test function must be uniquely named.
# 9. Do not include the target function (`{function_name}`) or any unrelated helper functions within the generated test code.
# 10. If testing edge cases, clearly handle potential side effects like recursion limits or large input sizes.

# Additional Notes:
# - Prioritize clarity and correctness in the generated test functions.
# - Focus on making tests self-contained and isolated from external dependencies.
# - Avoid excessive use of comments or unnecessary verbosity within the test code.
# - If the function interacts with external resources (e.g., files, network), mock those resources using libraries like `unittest.mock` or `pytest` fixtures.

# Example for a function 'add(a, b)' that adds two numbers:
# def test_add_positive_numbers():
#     ""Test adding two positive numbers.""
#     assert add(2, 3) == 5
#
# def test_add_zero():
#     ""Test adding zero to a number.""
#     assert add(0, 5) == 5
#
# def test_add_negative_numbers():
#     ""Test adding two negative numbers.""
#     assert add(-2, -3) == -5
#
# def test_add_mixed_sign_numbers():
#     ""Test adding a positive and a negative number.""
#     assert add(2, -3) == -1
#
# def test_add_invalid_string_inputs():
#     ""Test that the function raises a TypeError for string inputs.""
#     with pytest.raises(TypeError):
#         add("a", 1)
#
# def test_add_invalid_none_input():
#     ""Test that the function raises a TypeError for None input.""
#     with pytest.raises(TypeError):
#         add(None, 1)
#
# def test_add_large_numbers():
#     ""Test adding very large numbers.""
#     assert add(1_000_000, 2_000_000) == 3_000_000
#
# def test_add_small_fractional_numbers():
#     ""Test adding small fractional numbers.""
#     assert add(0.1, 0.2) == 0.3

# Your task:
# Generate the test cases below. Ensure the code adheres strictly to the guidelines above.
"""

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)

    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=1000,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id,
        num_return_sequences=1,
    )

    test_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return test_code

def post_process_test_code(test_code):
    """
    Post-process the generated test code to ensure validity.
    """
    try:
        lines = test_code.splitlines()
        processed_lines = [line.rstrip() for line in lines if line.strip()]
        return "\n".join(processed_lines)
    except Exception as e:
        print(f"Error during post-processing: {e}")
        return test_code

def validate_test_case(test_code):
    """
    Validate the generated test case by checking its syntax and structure.
    """
    try:
        print("Generated Raw Test Code:\n", test_code)  # Debug: Print raw code
        test_code = post_process_test_code(test_code)  # Post-process the code
        print("Post-Processed Test Code:\n", test_code)  # Debug: Print processed code
        compile(test_code, '<string>', 'exec')  # Validate syntax
        if "def " not in test_code:
            print("Validation failed: Missing function definitions.")
            return False
        if "assert" not in test_code and "pytest.raises" not in test_code:
            print("Validation failed: No 'assert' or 'pytest.raises' statements found.")
            return False
        return True
    except SyntaxError as e:
        print(f"Validation failed: {e}")
        return False

def analyze_code_and_generate_tests(file_path):
    """
    Analyze Python code and generate test cases for each function.
    Save the results to a new file and return its path.
    """
    if not file_path.endswith('.py'):
        raise ValueError(f"Unsupported file extension for file: {file_path}. Only .py files are supported.")

    with open(file_path, 'r') as f:
        code = f.read()

    functions = extract_functions(code)
    if not functions:
        raise ValueError("No functions found in the provided code.")

    print(f"Found functions: {functions}")
    test_cases = ""
    for func in functions:
        try:
            print(f"Processing function: {func}")
            func_code = extract_function_code(code, func)
            if not func_code:
                print(f"Skipping function {func} due to extraction issues.")
                continue

            function_purpose = extract_function_purpose(code, func)
            generated_test = generate_test_case(func, function_purpose)
            if validate_test_case(generated_test):
                test_cases += generated_test + "\n\n"
            else:
                print(f"Skipping invalid test case for function: {func}")
        except Exception as e:
            print(f"Error processing function {func}: {e}")

    base_name, ext = os.path.splitext(file_path)
    test_file_name = f"{base_name}_test{ext}"
    with open(test_file_name, 'w') as f:
        f.write(test_cases)

    return test_file_name

def remove_duplicate_tests(test_code):
    """
    Remove duplicate or redundant test cases from the generated code.
    """
    seen = set()
    unique_tests = []
    for line in test_code.splitlines():
        if line not in seen:
            unique_tests.append(line)
            seen.add(line)
    return "\n".join(unique_tests)


def process_file(file_path):
    """
    Main entry point for external calls to process a file and generate test cases.
    Returns the path to the generated test file.
    """
    try:
        return analyze_code_and_generate_tests(file_path)
    except Exception as e:
        raise RuntimeError(f"Error generating test cases: {e}")
