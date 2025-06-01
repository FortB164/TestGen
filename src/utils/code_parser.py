import re

def extract_function_names(code: str) -> list:
    """Extract function names from the code."""
    function_pattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
    function_names = re.findall(function_pattern, code)
    
    processed_names = []
    for name in function_names:
        if name.startswith('sum_of_'):
            processed_names.append('sum_of')
        elif name.startswith('average_of_'):
            processed_names.append('average_of')
        else:
            processed_names.append(name)
            
    return processed_names 