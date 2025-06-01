import os

# Base directory is the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration files
INSTRUCTIONS_PATH = os.path.join(os.path.dirname(__file__), 'instructions.txt')
FILES_LIST_PATH = os.path.join(os.path.dirname(__file__), 'programming_files_list.txt')

# Model settings
DEFAULT_MODEL = "starcoder:7b"
MODEL_CACHE_DIR = os.path.join(BASE_DIR, 'training_data', 'model_cache.json')

# Directory settings
SOURCE_SAMPLES_DIR = os.path.join(BASE_DIR, 'source_samples')
TEST_SAMPLES_DIR = os.path.join(BASE_DIR, 'test_samples')
TRAINING_DATA_DIR = os.path.join(BASE_DIR, 'training_data') 