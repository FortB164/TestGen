# TestGen

TestGen is an AI-powered test generation tool that uses Ollama to automatically generate test cases for Python code. It can work with both a base model and custom-trained models for improved test generation.

## Features

- **Automatic Test Generation**: Generate test cases for Python functions using AI
- **Model Training**: Train custom models using your own test samples
- **Model Caching**: Save and reuse trained models without retraining
- **Memory Efficient**: Optimized for low memory usage and high performance
- **User-Friendly Interface**: Simple CLI and GUI for file selection
- **Test Execution**: Automatically runs generated tests
- **Comprehensive Reporting**: Detailed test execution reports with pass rates and failure details

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TestGen.git
cd TestGen
```

2. Install dependencies:
```bash
pip install -e .
```

3. Ensure Ollama is installed and running on your system.

## Usage

### Basic Test Generation

Generate tests using the base model and run them:
```bash
python main.py --mode generate
```

### Skip Test Execution

Generate tests without running them:
```bash
python main.py --mode generate --skip-tests
```

### Using a Trained Model

Generate tests using a custom-trained model:
```bash
python main.py --mode generate --output-model my_trained_model
```

### Training a New Model

Train a new model using your test samples:
```bash
python main.py --mode train \
    --source-dir source_samples \
    --test-dir test_samples \
    --output-model my_trained_model
```

### Force Retraining

Update an existing model with new training data:
```bash
python main.py --mode train \
    --source-dir source_samples \
    --test-dir test_samples \
    --output-model my_trained_model \
    --force
```

### File Selection

Use the GUI to select files for test generation:
```bash
python main.py --mode select
```

## Project Structure

```
TestGen/
├── src/
│   ├── core/
│   │   ├── test_generator.py    # Test generation logic
│   │   └── model_trainer.py     # Model training functionality
│   ├── utils/
│   │   ├── file_handler.py      # File operations
│   │   ├── code_parser.py       # Code parsing utilities
│   │   └── test_runner.py       # Test execution and reporting
│   ├── config/
│   │   ├── settings.py          # Configuration settings
│   │   ├── instructions.txt     # Test generation instructions
│   │   └── programming_files_list.txt  # List of files to process
│   └── ui/
│       └── file_selector.py     # GUI for file selection
├── test_samples/                # Sample test files
├── source_samples/              # Sample source files
├── training_data/              # Training data and model cache
│   ├── model_cache.json        # Cache of trained models
│   └── training_examples.json  # Prepared training data
├── main.py                     # Entry point
└── setup.py                    # Package configuration
```

## Training Data

The `training_data` directory stores all data related to model training:

### Model Cache (`model_cache.json`)
- Stores information about trained models
- Contains metadata for each model:
  - Base model used
  - Training data used
  - Timestamp of training
- Enables model reuse without retraining
- Automatically updated when new models are trained

### Training Examples (`training_examples.json`)
- Stores prepared training data
- Created from source and test samples
- Contains pairs of:
  - Source code functions
  - Corresponding test cases
- Used for model fine-tuning
- Automatically generated during training

## Test Reports

TestGen provides comprehensive test execution reports that include:

### Per-File Results
- Total number of tests
- Pass rate percentage
- Number of failed tests
- Number of errors
- Number of skipped tests
- Detailed failure messages and tracebacks

### Overall Results
- Total number of test files
- Total number of tests
- Overall pass rate
- Total failures and errors
- Total skipped tests

Example report output:
```
=== Test Execution Report ===

Per-File Results:
--------------------------------------------------------------------------------

math_functions_test.py:
  Total Tests: 24
  Passed: 20 (83.3%)
  Failed: 2
  Errors: 2
  Skipped: 0

  Failures:
    - test_add_edge_1
      AssertionError: Expected 0, got 1

Overall Results:
--------------------------------------------------------------------------------
Total Files: 1
Total Tests: 24
Passed: 20 (83.3%)
Failed: 2
Errors: 2
Skipped: 0
--------------------------------------------------------------------------------
```

## How It Works

1. **Test Generation**:
   - Uses Ollama's AI model to analyze Python code
   - Generates comprehensive test cases including edge cases
   - Supports both basic and custom-trained models

2. **Model Training**:
   - Uses your test samples to train a custom model
   - Caches trained models for future use
   - Improves test generation quality over time

3. **Test Execution**:
   - Automatically runs generated tests
   - Captures test results and failures
   - Generates detailed execution reports

4. **Memory Optimization**:
   - Chunked file reading
   - Streaming responses
   - Efficient memory management
   - Cached model storage

## Requirements

- Python 3.7+
- Ollama
- pytest
- pytest-json-report

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 