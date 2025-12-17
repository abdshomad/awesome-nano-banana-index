import os
import re
from . import BaseExtractor

class PicoTrexExtractor(BaseExtractor):
    def extract(self):
        base_dir = "Awesome-Nano-Banana-images-PicoTrex"
        readme_path = os.path.join(base_dir, "README.md")
        if os.path.exists(os.path.join(base_dir, "README_en.md")):
            readme_path = os.path.join(base_dir, "README_en.md")
        count = 0
        
        if not os.path.exists(readme_path):
             print(f"Warning: File {readme_path} not found.")
             return 0

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Logic for PicoTrex:
        # Almost identical to Mickorix
        # ### 例 X: [Title](link) (by [@Author](link))
        
        case_pattern = re.compile(r'### (?:Case|Example|例) (\d+): (.*?)[（\(]by \[@(.*?)\]\((.*?)\)[）\)](.*?)(?=### (?:Case|Example|例)|\Z)', re.DOTALL)
        
        for match in case_pattern.finditer(content):
            case_id = match.group(1)
            raw_title = match.group(2).strip()
            author = match.group(3)
            author_url = match.group(4)
            body = match.group(5)

            # Clean title
            title = raw_title
            original_url = ""
            link_match = re.match(r'\[(.*?)\]\((.*?)\)', raw_title)
            if link_match:
                title = link_match.group(1)
                original_url = link_match.group(2)
            
            # Extract Image
            image_url = ""
            img_match = re.search(r'<img src="(.*?)"', body)
            if img_match:
                img_path = img_match.group(1)
                image_url = f"https://github.com/PicoTrex/Awesome-Nano-Banana-images/raw/main/{img_path}"

            # Extract Prompt
            prompt = ""
            code_match = re.search(r'```(?:text|json)?\n(.*?)\n```', body, re.DOTALL)
            if code_match:
                prompt = code_match.group(1)
                
            description = f"Example {case_id}: {title}"
            
            metadata = {
                "title": title,
                "author": author,
                "author_url": author_url,
                "original_url": original_url,
                "repo_url": "https://github.com/PicoTrex/Awesome-Nano-Banana-images",
                "image_url": image_url,
                "tags": ["picotrex", f"case-{case_id}"]
            }
            
            self.save_entry(metadata, description, prompt, f"picotrex-{case_id}-{title}", subdir="picotrex")
            count += 1
            
        return count
