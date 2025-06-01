import argparse
from src.core.test_generator import TestGenerator
from src.core.model_trainer import ModelTrainer
from src.ui.file_selector import select_and_filter_files
from src.utils.test_runner import TestRunner, TestReporter
from src.config.settings import TEST_SAMPLES_DIR

def main():
    """CLI entry point for processing multiple files and generating tests."""
    parser = argparse.ArgumentParser(description='Test Generator and Model Trainer')
    parser.add_argument('--mode', choices=['generate', 'train', 'select'], default='generate',
                      help='Mode to run in: generate tests, train model, or select files')
    parser.add_argument('--source-dir', help='Directory containing source Python files')
    parser.add_argument('--test-dir', help='Directory containing test Python files')
    parser.add_argument('--output-model', help='Name for the fine-tuned model')
    parser.add_argument('--model', default='starcoder:7b',
                      help='Base model to use (default: starcoder:7b)')
    parser.add_argument('--force', action='store_true',
                      help='Force retraining even if model exists')
    parser.add_argument('--skip-tests', action='store_true',
                      help='Skip running tests after generation')
    
    args = parser.parse_args()
    
    if args.mode == 'select':
        select_and_filter_files()
        return
        
    if args.mode == 'train':
        if not all([args.source_dir, args.test_dir, args.output_model]):
            print("Error: --source-dir, --test-dir, and --output-model are required for training mode")
            return
            
        trainer = ModelTrainer(args.model)
        
        # Check if model already exists
        if not args.force and trainer.get_trained_model(args.output_model):
            print(f"Model {args.output_model} already exists. Use --force to retrain.")
            return
        
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
        # Check if a custom model is specified
        model_name = args.model
        if args.output_model:
            trainer = ModelTrainer()
            if trainer.get_trained_model(args.output_model):
                model_name = args.output_model
                print(f"Using trained model: {model_name}")
            else:
                print(f"Trained model {args.output_model} not found. Using base model: {model_name}")
        
        generator = TestGenerator(model_name)
        try:
            generated_test_files = generator.process_files_list()
            print(f"Generated test files: {generated_test_files}")
            
            # Run tests if not skipped
            if not args.skip_tests and generated_test_files:
                print("\nRunning generated tests...")
                test_runner = TestRunner(TEST_SAMPLES_DIR)
                results = test_runner.run_tests(generated_test_files)
                TestReporter.print_report(results)
                
        except Exception as e:
            print(f"Error generating tests: {e}")

if __name__ == "__main__":
    main() 