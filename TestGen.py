from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import re

# Load the CodeGen model
model_name = "Salesforce/codegen-350M-mono"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def extract_functions(code):
    """
    Extract function definitions from Python code.
    """
    pattern = re.compile(r"def (\w+)\(.*\):")
    return pattern.findall(code)

def generate_test_case(function_name, function_code):
    """
    Generate test cases for a single function using the model.
    """
    prompt = f"""
# Generate test cases for the following function:
# Function name: {function_name}
# Code:
{function_code}

# Write the test cases below:
"""
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        inputs["input_ids"],
        max_length=300,
        temperature=0.5,
        top_p=0.8,
        eos_token_id=tokenizer.eos_token_id,
        num_return_sequences=1,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

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

    # Generate test cases for each function
    test_cases = ""
    for func in functions:
        func_code = extract_function_code(code, func)
        test_cases += generate_test_case(func, func_code) + "\n\n"

    # Save the test cases
    base_name, ext = os.path.splitext(file_path)
    test_file_name = f"{base_name}_test{ext}"
    with open(test_file_name, 'w') as f:
        f.write(test_cases)

    return test_file_name

def extract_function_code(code, function_name):
    """
    Extract the full code of a specific function by name.
    """
    pattern = re.compile(rf"(def {function_name}\(.*\):(?:\n    .*)*)", re.MULTILINE)
    match = pattern.search(code)
    return match.group(1) if match else ""

def process_file(file_path):
    """
    Main entry point for external calls to process a file and generate test cases.
    Returns the path to the generated test file.
    """
    try:
        return analyze_code_and_generate_tests(file_path)
    except Exception as e:
        raise RuntimeError(f"Error generating test cases: {e}")
