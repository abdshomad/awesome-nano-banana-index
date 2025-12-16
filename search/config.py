"""Configuration management for the search engine."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Meilisearch configuration
MEILISEARCH_URL = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_API_KEY = os.getenv("MEILISEARCH_API_KEY", "")

# Index configuration
INDEX_NAME = os.getenv("INDEX_NAME", "nano_banana_index")
SEARCH_RESULT_LIMIT = int(os.getenv("SEARCH_RESULT_LIMIT", "20"))

# Submodules configuration
SUBMODULES_DIR = BASE_DIR
GITMODULES_FILE = BASE_DIR / ".gitmodules"

# Supported file types
SUPPORTED_FILE_TYPES = {
    "yaml": [".yml", ".yaml"],
    "markdown": [".md"],
    "images": [".png", ".jpg", ".jpeg", ".webp"]
}

# Language mappings
LANGUAGE_MAPPINGS = {
    "zh": "Chinese",
    "en": "English",
    "both": "Both"
}
