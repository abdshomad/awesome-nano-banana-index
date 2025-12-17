import os
import re
from . import BaseExtractor

class CuighExtractor(BaseExtractor):
    def extract(self):
        readme_path = "awesome-nano-banana-prompts-cuigh/README.md"
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()

        # Regex to find cases
        # Pattern: ### Case \d+: [Title](Link) (by [Author](Link))
        # Then content until next ### Case
        
        case_pattern = re.compile(r'### Case (\d+): \[(.*?)\]\(.*?\)\s*\(by \[(.*?)\]\(.*?\)\)(.*?)(?=### Case|\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            case_id = match.group(1)
            title = match.group(2)
            author = match.group(3)
            body = match.group(4)
            
            # Extract Image
            image_url = ""
            img_match = re.search(r'<img src="(.*?)"', body)
            if img_match:
                img_path = img_match.group(1)
                # Adjust relative path to absolute URL if possible or keep relative
                # Assuming github raw structure
                image_url = f"https://github.com/lohyco/awesome-nano-banana-prompts-cuigh/raw/main/{img_path}"
            
            # Extract Prompt
            # Usually in a code block
            prompt = ""
            code_match = re.search(r'```(?:json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
            
            description = f"Case {case_id} from Awesome Nano Banana Prompts Cuigh"
            
            metadata = {
                "title": title,
                "author": author,
                "repo_url": "https://github.com/lohyco/awesome-nano-banana-prompts-cuigh",
                "image_url": image_url,
                "tags": ["cuigh", f"case-{case_id}"]
            }
            
            self.save_entry(metadata, description, prompt, f"cuigh-{case_id}-{title}", subdir="cuigh")
            count += 1
            
        return count
