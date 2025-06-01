import os
import json
import ollama
from typing import List, Dict, Tuple, Generator, Optional
from pathlib import Path
from ..utils.file_handler import read_file

class ModelTrainer:
    def __init__(self, model_name: str = "starcoder:7b"):
        """Initialize the model trainer with a specific Ollama model."""
        self.model_name = model_name
        self.training_data_path = 'training_data'
        self.model_cache_path = os.path.join(self.training_data_path, 'model_cache.json')
        self._load_model_cache()
        
    def _load_model_cache(self):
        """Load the model cache from disk."""
        self.model_cache = {}
        if os.path.exists(self.model_cache_path):
            try:
                with open(self.model_cache_path, 'r') as f:
                    self.model_cache = json.load(f)
            except Exception as e:
                print(f"Error loading model cache: {e}")
                self.model_cache = {}
    
    def _save_model_cache(self):
        """Save the model cache to disk."""
        os.makedirs(os.path.dirname(self.model_cache_path), exist_ok=True)
        with open(self.model_cache_path, 'w') as f:
            json.dump(self.model_cache, f, indent=2)
    
    def get_trained_model(self, model_name: str) -> Optional[str]:
        """Get a trained model if it exists."""
        return self.model_cache.get(model_name)
    
    def prepare_training_data(self, source_dir: str, test_dir: str) -> List[Dict]:
        """Prepare training data from source and test files using generators."""
        training_examples = []
        source_files = list(Path(source_dir).glob('**/*.py'))
        test_files = list(Path(test_dir).glob('**/*.py'))
        
        # Use a generator for file pairs to save memory
        for source_file, test_file in self._match_source_test_files(source_files, test_files):
            try:
                # Read files in chunks to save memory
                source_content = read_file(source_file)
                test_content = read_file(test_file)
                
                example = {
                    "instruction": "Generate test cases for the following Python function:",
                    "input": source_content,
                    "output": test_content
                }
                training_examples.append(example)
                
                # Clear memory after processing each pair
                del source_content
                del test_content
                
            except Exception as e:
                print(f"Error processing {source_file}: {e}")
        
        return training_examples
    
    def _match_source_test_files(self, source_files: List[Path], test_files: List[Path]) -> Generator[Tuple[Path, Path], None, None]:
        """Match source files with their corresponding test files using a generator."""
        for source_file in source_files:
            source_name = source_file.stem
            test_file = next((f for f in test_files if f.stem == f"{source_name}_test"), None)
            if test_file:
                yield source_file, test_file
            else:
                print(f"No matching test file found for {source_file}")
    
    def save_training_data(self, examples: List[Dict], output_file: str):
        """Save training examples to a JSON file with memory-efficient writing."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Use a generator to write examples one at a time
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('[\n')  # Start array
            for i, example in enumerate(examples):
                json.dump(example, f, indent=2)
                if i < len(examples) - 1:
                    f.write(',\n')
                else:
                    f.write('\n')
            f.write(']\n')  # End array
    
    def fine_tune_model(self, training_data_file: str, output_model_name: str):
        """Fine-tune the model using the prepared training data with streaming."""
        try:
            # Check if model already exists
            if output_model_name in self.model_cache:
                print(f"Model {output_model_name} already exists. Use --force to retrain.")
                return self.model_cache[output_model_name]
            
            # Read training data in chunks
            with open(training_data_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            config = {
                "model": self.model_name,
                "output_model": output_model_name,
                "training_data": training_data
            }
            
            # Use streaming for large responses
            response = ollama.create(
                model=output_model_name,
                path=training_data_file,
                config=config,
                stream=True
            )
            
            # Process response in chunks
            for chunk in response:
                if 'status' in chunk:
                    print(f"Training status: {chunk['status']}")
            
            # Cache the trained model
            self.model_cache[output_model_name] = {
                "base_model": self.model_name,
                "training_data": training_data_file,
                "timestamp": str(Path(training_data_file).stat().st_mtime)
            }
            self._save_model_cache()
            
            print(f"Fine-tuning completed. New model name: {output_model_name}")
            return response
            
        except Exception as e:
            print(f"Error during fine-tuning: {e}")
            raise 