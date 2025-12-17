import os
import abc
from typing import List, Dict, Optional
import yaml
import re

class BaseExtractor(abc.ABC):
    def __init__(self, output_dir="database"):
        self.output_dir = output_dir

    @abc.abstractmethod
    def extract(self):
        """Perform extraction and return count of items extracted."""
        pass

    def save_entry(self, metadata: Dict, description: str, prompt: str, filename_hint: str, subdir: str = ""):
        """Helper to save a database entry."""
        # Clean filename
        slug = re.sub(r'[^a-zA-Z0-9]', '-', filename_hint.lower()).strip('-')
        slug = re.sub(r'-+', '-', slug)
        if len(slug) > 200:
            slug = slug[:200]
        filename = f"{slug}.md"
        
        target_dir = self.output_dir
        if subdir:
            target_dir = os.path.join(self.output_dir, subdir)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        filepath = os.path.join(target_dir, filename)
        
        # Dont overwrite if exists? For now overwrite is fine or skip.
        # Let's overwrite to ensure updates propagate.
        
        content = "---\n"
        content += yaml.dump(metadata, sort_keys=False)
        content += "---\n\n"
        content += "## Description\n"
        content += f"{description}\n\n"
        content += "## Prompt\n"
        content += f"{prompt}\n"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
