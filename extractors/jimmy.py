import os
import re
from . import BaseExtractor

class JimmyLvExtractor(BaseExtractor):
    def extract(self):
        base_dir = "awesome-nano-banana-JimmyLv"
        readme_path = os.path.join(base_dir, "README.md")
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r') as f:
            content = f.read()

        # Logic for JimmyLv:
        # Headers: ### Case X: Title (by @Author)
        # Content: | Gemini | GPT-4o | tables, then **Prompt** code block.
        
        case_pattern = re.compile(r'### Case (\d+): ([^\n]+) \(by \[@(.*?)\]\(.*?\)\)(.*?)(?=### Case|\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            case_id = match.group(1)
            title = match.group(2)
            author = match.group(3)
            body = match.group(4)
            
            # Extract Image (Gemini column usually first)
            image_url = ""
            img_match = re.search(r'<img src="(.*?)"', body)
            if img_match:
                image_url = img_match.group(1)

            # Extract Prompt
            prompt = ""
            code_match = re.search(r'```(?:text|json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
            
            description = f"Case {case_id}: {title}"
            
            metadata = {
                "title": title,
                "author": author,
                "repo_url": "https://github.com/JimmyLv/awesome-nano-banana",
                "image_url": image_url,
                "tags": ["jimmylv", f"case-{case_id}"]
            }
            
            self.save_entry(metadata, description, prompt, f"jimmylv-{case_id}-{title}", subdir="jimmylv")
            count += 1
            
        return count
